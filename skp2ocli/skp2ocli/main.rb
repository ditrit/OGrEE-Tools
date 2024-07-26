require 'sketchup.rb'
require 'extensions.rb'

module Skp2ocli
  module OCliExport
    TOLERANCE = 1.0 # Define TOLERANCE constant

    def self.check_right_angles(entity)
      face = get_face(entity)
      return nil unless face.is_a?(Sketchup::Face)
      return nil unless face.edges.length == 4

      vertices = face.vertices
      return nil unless vertices.length == 4

      vectors = vertices.each_with_index.map do |vertex, i|
        next_vertex = vertices[(i + 1) % 4]
        vertex.position.vector_to(next_vertex.position)
      end

      angles = vectors.each_with_index.map do |vector, i|
        next_vector = vectors[(i + 1) % 4]
        angle_between_vectors(vector, next_vector)
      end

      angles.all? { |angle| (90 - angle).abs < TOLERANCE }
    end

    def self.get_face(entity)
      case entity
      when Sketchup::Face then entity
      when Sketchup::Edge then entity.faces.first
      when Sketchup::Vertex then entity.edges.map(&:faces).flatten.uniq.first
      else nil
      end
    end

    def self.angle_between_vectors(vector1, vector2)
      dot_product = vector1.dot(vector2)
      magnitudes = vector1.length * vector2.length
      Math.acos(dot_product / magnitudes).radians
    end

    def self.is_square?(face)
      return false unless face.is_a?(Sketchup::Face) && face.edges.length == 4
      vertices = face.vertices
      return false unless vertices.length == 4

      vectors = vertices.each_with_index.map do |vertex, i|
        next_vertex = vertices[(i + 1) % 4]
        vertex.position.vector_to(next_vertex.position)
      end

      lengths = vectors.map(&:length)
      lengths.uniq.length == 1
    end

    def self.face_and_adjacent_are_squares?(face)
      return false unless is_square?(face)
      adjacent_faces = face.edges.flat_map(&:faces).uniq - [face]
      adjacent_faces.all? { |adjacent_face| is_square?(adjacent_face) }
    end

    def self.calculate_total_edge_length(entity)
      case entity
      when Sketchup::Group, Sketchup::ComponentInstance
        entity.definition.entities.grep(Sketchup::Edge).map { |e| e.length.to_i }
      when Sketchup::Face
        entity.edges.map { |edge| edge.length.to_i }
      when Sketchup::Edge
        [entity.length.to_i]
      when Sketchup::Entities
        entity.grep(Sketchup::Edge).map { |e| e.length.to_i }
      else
        []
      end
    end

    def self.entities_intersect?(entity1, entity2)
      entity1.bounds.intersect(entity2.bounds).valid?
    end

    def self.check_intersection(selected_entity, all_entities)
      all_entities.reject { |entity| entity == selected_entity || entity.parent == selected_entity }
                  .select { |entity| entities_intersect?(selected_entity, entity) }
                  .uniq
    end

    def self.get_entity_coordinates(entity, transform)
      origin = Geom::Point3d.new(0, 0, 0)
      local_origin = origin.transform(transform)
      global_origin = entity.transformation * origin
      {
        local: local_origin.to_a.map(&:to_i),
        global: global_origin.to_a.map(&:to_i)
      }
    end

    def self.get_entity_identifier(entity)
      entity_tag = entity.layer.display_name
      entity_definition = entity.definition.name if entity.respond_to?(:definition)
      "Definition: #{entity_definition}, Tag: #{entity_tag}"
    end

    def self.get_entity_details(child_entity)
      details = {
        "type": child_entity.typename,
      }
      case child_entity
        when Sketchup::Face
          details["points"] = child_entity.vertices.map(&:position).map(&:to_a)  # Get vertex positions as arrays
          details["material"] = child_entity.material ? child_entity.material.name : nil  # Material name (if available)
        when Sketchup::Edge
          details["start_point"] = {
            "x": child_entity.start.position.x,
            "y":child_entity.start.position.y,
            "z":child_entity.start.position.z, 
          } # Start point position
          details["end_point"] = {
            "x": child_entity.end.position.x,
            "y":child_entity.end.position.y,
            "z":child_entity.end.position.z, 
          }    # End point position
          details["length"] = child_entity.length
        # Add cases for other geometry types (arc, solid, etc.) with their specific details
        when Sketchup::Group
          details["material"] = child_entity.material ? child_entity.material.name : nil  # Material name (if available)
          entities_details = []
          child_entity.definition.entities.each do |child_entity|
            # Get details of each child entity
            # here error below
            child_details = get_entity_details(child_entity)
            # Get the component's origin (outside the loop)
            entities_details << child_details
          end
          details["entities"] = entities_details
      end
      return details
    end

    def self.extract_children_entities(entity)
      # return empty list if no children
      definition = entity.definition
      if not definition.entities
        return []
      else
        entities_details = []
        definition.entities.each do |child_entity|
          # Get details of each child entity
          entities_details << get_entity_details(child_entity)
        end
        return entities_details
      end
    end

    def self.extract_model_objects(model)
      # Initialize empty array to store component data
      objects = []
      model.entities.each do |entity|
        # Check if entity is a component instance
        next unless entity.is_a?(Sketchup::ComponentInstance) or entity.is_a?(Sketchup::Group)

        # Get the component definition
        definition = entity.definition

        # Collect component details
        component_data = {
          "name": definition.name,
          "description": definition.description,
          "exact_position": entity.transformation.origin,  # Get transformation for component instance
        }
        component_data["position"] =  {
          "x":entity.transformation.origin.x, 
          "y":entity.transformation.origin.y, 
          "z":entity.transformation.origin.z
        }
        # get children entities
          component_data["entities"] = extract_children_entities(entity)
        # Store component data
        objects << component_data
      end
      return objects
    end

    def self.export(data, path)
      File.open(path, "w") do |file|
        # Write the JSON data to the file
        file.write(JSON.pretty_generate(data))
        puts "Data exported successfully to #{path}"
      end
    end

    unless file_loaded?(__FILE__)
      menu = UI.menu('Plugins')
      menu.add_item('Generate OCLI files') {
        model = Sketchup.active_model
        selection = model.selection
        entities = model.entities

        if selection.empty?
          UI.messagebox("Please select a single face!")
          return
        end

        selected_entity = selection.first
        angles = check_right_angles(selected_entity)

        if angles.nil?
          puts "Failed to check object 3D shape"
        else
          total_length = calculate_total_edge_length(selected_entity)
          puts "Total length of all edges: #{total_length}"

          if angles && total_length.uniq.size == 1
            puts "All edges of the selected entity are equal and all angles are 90 degrees. A cube"
            #UI.messagebox("Cube")
          elsif angles && total_length.uniq.size != 1
            puts "Edges of the selected entity are not all equal but all angles are 90 degrees. A cuboid"
            #UI.messagebox("Cuboid")
          else
            puts "Edges of the selected entity are not all equal and all the angles are not 90 degrees"
            #UI.messagebox("Unknown")
          end
        end

        parent_component = selected_entity
        while parent_component.parent.is_a?(Sketchup::Entities)
          parent_component = parent_component.parent
        end

        unless parent_component.is_a?(Sketchup::ComponentInstance) || parent_component.is_a?(Sketchup::Group)
          UI.messagebox("Please select an entity within a component or group.")
          return
        end

        selected_entity_identifier = get_entity_identifier(parent_component)

        all_entities = entities.grep(Sketchup::Group) + entities.grep(Sketchup::ComponentInstance)
        intersecting_entities = check_intersection(parent_component, all_entities)

        if intersecting_entities.empty?
          puts "No intersections found with the selected entity."
        else
          puts "##################"
          intersecting_entities.each do |entity|
            intersecting_entity_identifier = get_entity_identifier(entity)

            transform = entity.transformation.inverse * parent_component.transformation

            coords = get_entity_coordinates(parent_component, transform)

            puts "Selected entity (#{selected_entity_identifier}):"
            puts "  Global coordinates (origin 0,0,0): #{coords[:global]}"
            puts "  Local coordinates relative to intersecting entity (#{intersecting_entity_identifier}): #{coords[:local]}"
          end
          puts "#{intersecting_entities.size} intersecting entities found."
          puts "##################"
        end
        
        ## below implementation to export data in json format
        ## Create the JSON hash with additional information (optional)
        ## Uncomment the following lines if you wan to generate and export data in JSON format
        # exportable = { "model_name": model.name, "entities": extract_model_objects(model) }
        # puts exportable
        # filename = "diameters.json"
        # output_path = File.join("<path where to export the json", filename)
        # export(exportable, output_path)
      }
      file_loaded(__FILE__)
    end
  end
end
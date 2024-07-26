# This Plugin will automatically generate a JSON file containing the
# details about the components of the Sketchup Model
#
# * sketchup.rb is needed for `file_loaded?` and `file_loaded`.
#
# * extensions.rb is needed for the `SketchupExtension` class.

require "sketchup.rb"
require "extensions.rb"

module Skp2ocli
  module OCliExport
    # The use of `file_loaded?` here is to prevent the extension from being
    # registered multiple times. This can happen for a number of reasons when
    # the file is reloaded - either when debugging during development or
    # extension updates etc.
    #
    # The `__FILE__` constant is a "magic" Ruby constant that returns a string
    # with the path to the current file. You don't have to use this constant
    # with `file_loaded?` - you can use any unique string to represent this
    # file. But `__FILE__` is very convenient for this.
    unless file_loaded?(__FILE__)
      ex = SketchupExtension.new('Generate OCLI files', 'skp2ocli/main')
      ex.description = "Generate OCLI file that works with OGREE from Sketchup model."
      ex.version     = "0.0.1"
      ex.copyright   = "#{ex.creator} 2024"
      ex.creator     = "Kais BETTAIEB"
      Sketchup.register_extension(ex, true)

      # This is needed for the load guard to prevent the extension being
      # registered multiple times.
      file_loaded(__FILE__)
    end
  end #end OCliExport
end # end Skp2ocli
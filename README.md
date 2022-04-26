# OGREE-Tools
Repository for the tools used in OGrEE.


# How to use with git
## Clone the repo

```
git clone https://github.com:ditrit/OGrEE-Tools.git
```

## Switch to the appropriate dev branch
You need to provide a file (named .env) containing all of the API parameters as below:

Axel
```
git checkout -b dev-FBX
```
Hervé
```
git checkout -b dev-domain
```
Vincent
```
git checkout -b dev-label
```

## Stage, commit and push when modifications are done
Run the following commands:
```
git add .
git commit -m "Your commit message"
git push
```

You can also use the graphical interface of VS Code. 

## Merge with the main branch
First click on the "X branches" button:

![Main Window](/image_readme/avant%20merge.PNG)

Then click on "new pull request":

![Pull Request Window](/image_readme/merge.PNG)

You can then compare and merge the dev branch into the main one:

![Compare Window](/image_readme/compare.PNG)

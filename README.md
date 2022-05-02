# OGREE-Tools
Repository for the tools used in OGrEE.


# How to use with git
## Clone the repo

```
git clone https://github.com/ditrit/OGrEE-Tools.git
```
## Switch to the right branch

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
```
Then you need to push on the right remote branch:
```
git push https://<token>@github.com/<repo>
```
You can also use the graphical interface of VS Code or any editor.

## FOR FIRST TIME PUSH

You need to specify the remote branch you want to push on:

Axel
```
git push --set-upstream origin dev-FBX
```
Hervé
```
git push --set-upstream origin dev-domain
```
Vincent
```
git push --set-upstream origin dev-label
```
Then login with the pop-up window to finalize the push:

![Login Window](/image_readme/login.PNG)

If you have any issue, please follow the instructions on the following URL : https://unityatscale.com/unity-version-control-guide/how-to-setup-unity-project-on-github/
## Merge with the main branch
First click on the "X branches" button:

![Main Window](/image_readme/avant%20merge.PNG)

Then click on "new pull request":

![Pull Request Window](/image_readme/merge.PNG)

You can then compare and merge the dev branch into the main one:

![Compare Window](/image_readme/compare.PNG)

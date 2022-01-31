files=$(git diff --name-only HEAD HEAD~1)

#I'm trying to make a script that will get the version nams
# from the changelogs to pass ot a gh action
for file in $files
do
    IFS='/' read -ra arr <<< "$file"
    VERSION=lnlnlnlf

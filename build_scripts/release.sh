#!/bin/bash

# Git Info
# ---------
#
# the repo also depends on two submodules, to initialize run the following::
#
#     git clone https://github.com/stephanwaz/craytraverse
#     cd craytraverse
#     git submodule init
#     git submodule update --remote
#     git -C src/Radiance config core.sparseCheckout true
#     cp src/sparse-checkout .git/modules/src/Radiance/info/
#     git submodule update --remote --force src/Radiance
#
# after a "git pull" make sure you also run::
#
#     git submodule update
#
# to track with the latest commit used by craytraverse.

printf "\n#######################################################\n"
echo have you confirmed that directory is ready for release?
echo make sure docker is running...
echo bash build_scripts/dist_check.sh
echo update HISTORY.rst
echo git commit


printf "#######################################################\n\n"
echo if you are giving an explicit version have you run bumpversion?
printf "REMOVE 'dev' from version tag (find/replace)\n"
printf "#######################################################\n\n"

echo -n "proceed to release (y/n)? "
read -r answer

if [ "$answer" != "${answer#[Yy]}" ] ;then
    clean=$(git status --porcelain --untracked-files=no | wc -l)
    if [ "$clean" -lt 1 ]; then
        if [[ $# == 1 && ($1 == "patch" || $1 == "minor" || $1 == "major" || $1 == v*.*.*) ]]; then
            if [[ $1 == v*.*.* ]]; then
                git tag -a "$1" -m "tagged for release $1"
            else
                bumpversion --tag --commit "$1"
            fi
            bash build_scripts/dist_versions.sh
            echo -n "ok to push (y/n)? "
            read -r answer
            if [ "$answer" != "${answer#[Yy]}" ] ;then
                twine upload dist/*.tar.gz dist/*.whl
                git push
                tag="$(git tag | tail -1)"
                git push origin $tag
			else
				git status
			fi
        else
            echo usage: ./release.sh "[patch/minor/major]"
            echo usage: ./release.sh "vX.X.X (assumes bumpversion has already been run and vX.X.X matches"
        fi
    else
        echo working directory is not clean!
        git status --porcelain --untracked-files=no
    fi
else
    echo aborted
fi



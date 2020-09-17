# Updating requirements

If you are creating a conda environment YAML file from an existing file, you may want to update all (or most) of the packages to the most recent versions. This is trickier than it might seem, since you ideally want to compile the requirements from inside the runtime container. Here is a workflow to accomplish that, along with a few helpful scripts. (This typically only needs to be done once at the beginning of the competition.)

First, remove all of the version pins from the existing `py-cpu.yml`.

```bash
sed -i 's/=.*$//' runtime/py-cpu.yml
```

You can edit `py-cpu.yml` to manually pin any desired versions.

Now, build the container. In the process of creating the conda environment, conda will perform dependency resolution to compile your unpinned dependencies to pinned dependencies. Export the environment file (including pinned dependencies) and save out to a file.

```bash
docker build -t deid2/codeexecution runtime
docker run \
       -a stdout \
       deid2/codeexecution \
       /bin/bash -c "conda env export -n py-cpu" \
    > runtime/py-cpu.yml
```

The resulting `py-cpu.yml` is a _complete_ list of the packages in your environment (including subdependencies of the packages you specified). While this is great for reproducibility, it is a bit overdetermined―it increases the chance that any new package added will have a dependency conflict with the existing pinned packages. It is better to only pin the versions of the top-level packages you want, and then let conda dependency resolver find subdependencies that work with everything. Manually edit `py-cpu.yml` to only include the pinned versions of the partial list of top-level packages you want to include.

/* PROMUS-FIND

Usage: 

    promus-find dir pattern1 patter2 ...

Description:

    Unlike `find` which prints all the absolute paths of those files
    that match a particular pattern, promus-find only prints the path
    to the directory containing an instance of a file which matches a
    pattern.

Examples:

    Compare the outputs of the following (replacing the paths of
    course):

        promus-find /User/jmlopez/test *.zip

        find /User/jmlopez/test -name *.zip

    Note that `find` will warn you if it was not able to access a
    directory. `promus-find` will simply ignore this and proceed
    looking for directories containing files with matching patterns.

Note:

    To find more than directories matching more than one pattern
    simply add more patterns to it. i.e.

        promus-find dir pattern1 pattern2

        find dir -name pattern1 -o -name pattern2

Author: [Manuel Lopez](http://jmlopez-rod.github.io/)
Contact: <jmlopez.rod@gmail.com>
Copyright 2013 Jose Manuel Lopez

*/

#include <dirent.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fnmatch.h>

bool include_dir(int index, const char* path, int num, const char* files[]) {
    /* Traverses `path` and looks for files that maches any of the
    strings in `files`. Here `num` is the number of strings in
    `files` and index is the number of characters to avoid printing
    in the path.

    Note: The `readdir` function does not guarantee an order. As soon
    as it is known that a directory contains any of the files we
    print it. */
    char subdir[1000];
    DIR* dir = opendir(path);
    if (dir == NULL) return false;
    struct dirent *entry = readdir(dir);
    bool found = false;
    bool in_sub = false;
    bool include = false;
    while (entry != NULL) {
        if (entry->d_name[0] != '.' && entry->d_type == DT_DIR) {
            for (int i=0; i < num; ++i) {
                if (fnmatch(files[i], entry->d_name, FNM_PERIOD) == 0) {
                    if (path[index] == '/') {
                        printf("%s/%s/*\n", path+index+1, entry->d_name);
                    } else {
                        printf("%s/*\n", entry->d_name);
                    }
                    include = true;
                    break;
                }
            }
            if (!include) {
                sprintf(subdir, "%s/%s", path, entry->d_name);
                if (include_dir(index, subdir, num, files)) {
                    in_sub = true;
                }
            }
        } else if (!in_sub && !found) {
            for (int i=0; i < num; ++i) {
                if (fnmatch(files[i], entry->d_name, FNM_PERIOD) == 0) {
                    if (path[index] == '/') {
                        printf("%s\n", path+index+1);
                    }
                    found = true;
                    break;
                }
            }
        }
        entry = readdir(dir);
        include = false;
    }
    if (!found && in_sub && path[index] == '/') {
        printf("%s\n", path+index+1);
    }
    closedir(dir);
    return found || in_sub;
}

int main(int argc, const char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: promus-find dir pattern1 pattern2 ... \n");
        return 1;
    }
    include_dir(strlen(argv[1]), argv[1], argc-2, argv+2);
    return 0;
}

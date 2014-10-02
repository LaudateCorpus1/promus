module.exports = function(grunt) {
    'use strict';
    // Force use of Unix newlines
    grunt.util.linefeed = '\n';
    // Project configuration.
    grunt.initConfig({
        // Metadata.
        dest: '../static',
        pkg: grunt.file.readJSON('package.json'),
        banner: '/* <%= pkg.name %> v<%= pkg.version %> | For license and credit attribution\n' +
        '   see <%= pkg.license.url %> */\n',
        // Task configuration.
        csslint: {
            options: {
                csslintrc: 'less/.csslintrc'
            },
            src: [
                '<%= dest %>/css/<%= pkg.name %>.css',
            ]
        },
        concat: {
            options: {
                banner: '<%= banner %>\n',
                stripBanners: true
            },
            pkgname: {
                src: [
                    'js/jquery-1.11.0.js',
                    'js/bootstrap/transition.js',
                    'js/bootstrap/alert.js',
                    'js/bootstrap/button.js',
                    'js/bootstrap/carousel.js',
                    'js/bootstrap/collapse.js',
                    'js/bootstrap/dropdown.js',
                    'js/bootstrap/modal.js',
                    'js/bootstrap/tooltip.js',
                    'js/bootstrap/popover.js',
                    'js/bootstrap/scrollspy.js',
                    'js/bootstrap/tab.js',
                    'js/bootstrap/affix.js'
                ],
                dest: '<%= dest %>/js/<%= pkg.name %>.js'
            }
        },
        uglify: {
            options: {
                report: 'min'
            },
            pkgname: {
                options: {
                    banner: '<%= banner %>'
                },
                src: '<%= concat.pkgname.dest %>',
                dest: '<%= dest %>/js/<%= pkg.name %>.min.js'
            }
        },
        less: {
            compileCore: {
                options: {
                    strictMath: true,
                    sourceMap: true,
                    outputSourceFiles: true,
                    sourceMapURL: '<%= pkg.name %>.css.map',
                    sourceMapFilename: '<%= dest %>/css/<%= pkg.name %>.css.map'
                },
                files: {
                    '<%= dest %>/css/<%= pkg.name %>.css': 'less/<%= pkg.name %>.less'
                }
            },
            minify: {
                options: {
                    cleancss: true,
                    report: 'min'
                },
                files: {
                    '<%= dest %>/css/<%= pkg.name %>.min.css': '<%= dest %>/css/<%= pkg.name %>.css',
                }
            }
        },
        usebanner: {
            dist: {
                options: {
                    position: 'top',
                    banner: '<%= banner %>'
                },
                files: {
                    src: [
                        '<%= dest %>/css/<%= pkg.name %>.css',
                        '<%= dest %>/css/<%= pkg.name %>.min.css',
                    ]
                }
            }
        },
        csscomb: {
            options: {
                config: 'less/.csscomb.json'
            },
            dist: {
                files: {
                    '<%= dest %>/css/<%= pkg.name %>.css': '<%= dest %>/css/<%= pkg.name %>.css',
                }
            }
        }
    });
    // These plugins provide necessary tasks.
    require('load-grunt-tasks')(grunt, {scope: 'devDependencies'});
    // JS compilation task.
    grunt.registerTask('js', ['concat']);
    // CSS compilation task.
    grunt.registerTask('css', ['less:compileCore', 'csscomb']);
    // JS distribution task.
    grunt.registerTask('dist-js', ['concat', 'uglify']);
    // CSS distribution task.
    grunt.registerTask('dist-css', ['less', 'csscomb', 'usebanner']);
    // Full distribution task.
    grunt.registerTask('dist', ['dist-css', 'csslint', 'dist-js']);
    // Default task.
    grunt.registerTask('default', ['dist']);
};

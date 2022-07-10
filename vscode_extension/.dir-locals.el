((typescript-mode . ((eval . (progn
                               (with-eval-after-load 'lsp-mode
                                 (setq lsp-file-watch-ignored-directories
                                       (cl-remove-duplicates
                                        (append lsp-file-watch-ignored-directories
                                                '("[/\\\\]node_modules\\'"
                                                  "[/\\\\]out\\'"
                                                  "[/\\\\].vscode\\'"
                                                  "[/\\\\].vscode-test\\'")))))
                               (with-eval-after-load 'projectile
                                 (projectile-register-project-type 'yarn '("package.json")
                                                                   :project-file "package.json"
                                                                   :compile "yarn compile"
                                                                   :src-dir "src/"
                                                                   :test "yarn test"
                                                                   :test-dir "src/test/suite/"
                                                                   :test-suffix ".test"))))
                     (projectile-create-missing-test-files . t)
                     (projectile-project-type . yarn)
                     (fill-column . 127))))

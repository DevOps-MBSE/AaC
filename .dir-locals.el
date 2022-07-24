((nil . ((projectile-create-missing-test-files . t)))
 (python-mode . ((eval . (progn
                           (with-eval-after-load 'lsp-mode
                             (setq lsp-file-watch-ignored-directories
                                   (cl-remove-duplicates
                                    (append lsp-file-watch-ignored-directories
                                            '("[/\\\\]__pycache__\\'"
                                              "[/\\\\]\\.venv\\'"
                                              "[/\\\\]\\.eggs\\'"
                                              "[/\\\\]build\\'"
                                              "[/\\\\]model\\'"
                                              "[/\\\\]html_code_coverage\\'"
                                              "[/\\\\]\\.mypy_cache\\'"
                                              "[/\\\\]\\.tox\\'")))))))
                 (projectile-project-type . python-pkg)
                 (projectile-project-test-cmd . "cd python; source .venv/bin/activate.fish && flake8 . && nose2 -c tox.ini")
                 (python-backend . lsp)
                 ;; To use this, add the `pyright` LSP server with `yarn global add pyright`.
                 (python-lsp-server . pyright)
                 ;; (python-lsp-server . pylsp)
                 (python-formatter . black)
                 (python-test-runner . nose)
                 (python-fill-column . 127)
                 (python-tab-width . 4)
                 (python-format-on-save . nil)
                 (python-sort-imports-on-save . nil)
                 (blacken-line-length . 'fill)))
 (typescript-mode . ((eval . (progn
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
                     (projectile-project-type . yarn)
                     (fill-column . 127))))
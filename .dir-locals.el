((nil . ((projectile-project-name . "aac")
         (projectile-create-missing-test-files . t)))
 (python-mode . ((eval . (progn
                           (add-to-list 'load-path (projectile-project-root) t)
                           (require 'aac)
                           (aac-add-debug-templates-from-code-workspace)
                           (advice-add 'projectile-test-directory :around #'aac-projectile-test-dir)))
                 (projectile-default-test-directory . "tests/")
                 (projectile-project-type . python-pkg)
                 (projectile-project-test-cmd . "cd python; flake8 . && nose2 -c tox.ini")
                 (python-backend . lsp)
                 (python-lsp-server . pyright)
                 (python-formatter . black)
                 (python-test-runner . nose)
                 (python-fill-column . 127)
                 (python-tab-width . 4)
                 (python-format-on-save . nil)
                 (python-sort-imports-on-save . nil)
                 (blacken-line-length . fill)))
 (typescript-mode . ((eval . (with-eval-after-load 'projectile
                               (projectile-register-project-type 'yarn '("package.json")
                                                                 :project-file "package.json"
                                                                 :compile "yarn compile"
                                                                 :src-dir "src/"
                                                                 :test "yarn test"
                                                                 :test-dir "src/test/suite/"
                                                                 :test-suffix ".test")))
                     (projectile-project-type . yarn)
                     (fill-column . 127))))

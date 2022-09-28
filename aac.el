(defvar aac-added-launch-templates-p nil
  "Whether the launch.json run templates have been added, or not.")

(defun aac-modify-workspace-root-folder (type value)
  "Update the workspace folder with the appropriate subdirectory depending on the major mode."
  (string-replace
      "${workspaceFolder}"
      (string-join (list (projectile-project-root) type) f--path-separator)
      value))

(defun aac-add-debug-templates-from-code-workspace ()
  "Add launch configurations as debug templates from the appropriate code workspace."
  (require 'dap-mode)
  (let* ((launch-json (cdar (dap-launch-find-parse-launch-json)))
         (launch-configs (getf (getf launch-json :launch) :configurations)))
    (unless aac-added-launch-templates-p
      (dolist (type '("python"))
        (mapcar (lambda (config)
                  (let ((new-config))
                    (cl-dolist (pair (cl--plist-to-alist config))
                      (let ((key (car pair)) (val (cdr pair)))
                        (push key new-config)
                        (push (cl-typecase val
                                (string (aac-modify-workspace-root-folder type val))
                                (vector (map 'vector (lambda (v) (aac-modify-workspace-root-folder type v)) val))
                                (t val))
                              new-config)))
                    (setq config (reverse new-config))
                    (dap-register-debug-template (string-join (list type (getf config :name)) " :: ") config)))
                launch-configs)))
    (setq aac-added-launch-templates-p t)))

(defun aac-projectile-test-dir (projectile-test-directory-fn project-type)
  "AaC stores tests in tests/ not test/."
  (if (and (string-equal "aac" (projectile-project-name))
           (string-prefix-p "python" (symbol-name project-type)))
      "tests/"
      (projectile-test-directory-fn project-type)))

(with-eval-after-load 'projectile
  (projectile-register-project-type 'yarn '("package.json")
                                    :project-file "package.json"
                                    :compile "yarn compile"
                                    :src-dir "src/"
                                    :test "yarn test"
                                    :test-dir "src/test/suite/"
                                    :test-suffix ".test"))

(with-eval-after-load 'lsp-mode
  (setq lsp-file-watch-ignored-directories
        (cl-remove-duplicates
          (append lsp-file-watch-ignored-directories
                  ;; Python ignored directories
                  '("[/\\\\]__pycache__\\'"
                    "[/\\\\]\\.venv\\'"
                    "[/\\\\]\\.eggs\\'"
                    "[/\\\\]build\\'"
                    "[/\\\\]model\\'"
                    "[/\\\\]html_code_coverage\\'"
                    "[/\\\\]\\.mypy_cache\\'"
                    "[/\\\\]\\.tox\\'")

                  ;; JS/TS ignored directories
                  '("[/\\\\]node_modules\\'"
                    "[/\\\\]out\\'"
                    "[/\\\\].vscode\\'"
                    "[/\\\\].vscode-test\\'")))))

(with-eval-after-load 'dap-mode
  (require 'dap-variables)
  (advice-add 'dap-launch-find-launch-json :around
    (lambda (fn &rest args)
      (let ((root (projectile-project-root)))
        (cl-case major-mode
          (python-mode (dap-variables-find-vscode-config "python.code-workspace" root))
          (typescript-mode (dap-variables-find-vscode-config "vscode_extension.code-workspace" root))
          (t (apply fn args)))))))

(provide 'aac)

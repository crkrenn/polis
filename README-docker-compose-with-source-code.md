test new npm command: works! (add client-admin and client-report)
add docker compose variable and overlay

ARG default_app_arg=production
CMD ["myapp", "$default_app_arg"]

version: '3'
services:
  web:
    build:
      args:
        ARG2: newvalue2

(base) crkrenn@admins-MBP-2 crkrenn_clean % grep -e "webpack.*mode" */package.json
client-admin/package.json:    "build:dev": "webpack --mode=development",
client-admin/package.json:    "build:prod": "webpack --mode=production",
client-admin/package.json:    "analyze": "webpack --mode=production --analyze",
client-admin/package.json:    "dev": "webpack-dev-server --mode=development",
client-participation/package.json:    "analyze": "webpack --mode=production --analyze",
client-participation/package.json:    "build:dev": "webpack --mode=development",
client-participation/package.json:    "build:prod": "webpack --mode=production"
client-report/package.json:    "bundle:prod": "webpack --mode=production",
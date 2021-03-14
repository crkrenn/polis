* working on client-admin/dev-server

* remove "get" functions from server/config.js

* figure out GOOGLE_APP_CREDS in server/src/comment.js

crkrenn@CRK-dGPS-MacBook-Pro --- source/polisServer ‹debug/node-convict-2* M?› » 
$ grep -n -i -e process.env -e polisConfig -R * | wc  
     120     578   10182

crkrenn@CRK-dGPS-MacBook-Pro --- source/polisServer ‹debug/node-convict-2* M?› » 
$ grep -n -i -e process.env -e polisConfig -R -l *                                                                   130 ↵
client-admin/.bundlewatch.config.js
client-admin/dev-server.js
client-admin/webpack.config.js
client-admin/webpack.config.unminified.js
client-admin/gulpfile.js
client-participation/Gruntfile.js
client-participation/webpack.config.js
client-participation/webpack.config.dev.js
client-participation/gulpfile.js
client-report/server.js
client-report/dev-server.js
client-report/webpack.config.js
client-report/webpack.config.dev.js
client-report/gulpfile.js
client-report/src/store/index.js
config/export_config.js
config/config.js
config/package.json
file-server/app.js
server/app.js
server/src/session.js
server/src/server.js
server/src/utils/cookies.js
server/src/config.js
server/src/comment.js
server/src/db/pg-query.js
server/src/email/senders.js

* make DEV start; debug error in server
* ask GPT fix errors, given two compose files

polis-test-server-1       |
polis-test-server-1       | up to date, audited 405 packages in 2s
polis-test-server-1       |
polis-test-server-1       | 6 packages are looking for funding
polis-test-server-1       |   run `npm fund` for details
polis-test-server-1       |
polis-test-server-1       | 52 vulnerabilities (1 low, 19 moderate, 26 high, 6 critical)
polis-test-server-1       |
polis-test-server-1       | To address issues that do not require attention, run:
polis-test-server-1       |   npm audit fix
polis-test-server-1       |
polis-test-server-1       | To address all issues possible (including breaking changes), run:
polis-test-server-1       |   npm audit fix --force
polis-test-server-1       |
polis-test-server-1       | Some issues need review, and may require choosing
polis-test-server-1       | a different dependency.
polis-test-server-1       |
polis-test-server-1       | Run `npm audit` for details.
polis-test-nginx-proxy-1  | 2023/08/10 19:13:59 [error] 32#32: *1 connect() failed (111: Connection refused) while connecting to upstream, client: ::ffff:172.26.0.1, server: _, request: "GET /api/v3/math/pca2?conversation_id=7xyebnynzz&cacheBust=45009994 HTTP/1.1", upstream: "http://172.26.0.6:5000/api/v3/math/pca2?conversation_id=7xyebnynzz&cacheBust=45009994", host: "localhost", referrer: "http://localhost/7xyebnynzz"
polis-test-nginx-proxy-1  | ::ffff:172.26.0.1 - - [10/Aug/2023:19:13:59 +0000] "GET /api/v3/math/pca2?conversation_id=7xyebnynzz&cacheBust=45009994 HTTP/1.1" 502 559 "http://localhost/7xyebnynzz" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36" "-"
polis-test-server-1       |
polis-test-server-1       | > polis@0.0.0 build:watch
polis-test-server-1       | > tsc --watch & nodemon --inspect=0.0.0.0:9229 dist/app.js
polis-test-server-1       |
polis-test-server-1       | sh: nodemon: not found
polis-test-server-1       | sh: tsc: not found
polis-test-server-1 exited with code 127

.PHONY: start start-debug stop clean test test-list test-one restart-one help

# $SUDO is an optional shell variable which can be set to "sudo" if needed
# (for example, on an ec2 instance)

help:
	@echo "help                   --- Show this list."
	@echo "restart                --- make stop; make start"
	@echo "restart-one            --- make stop-one <one>; make start-one <one>"
	@echo "start                  --- Run 'docker-compose up --build -d'."
	@echo "start-one              --- Run 'docker-compose up --build -d <one>'."
	@echo "start-debug            --- Run 'docker-compose --log-level DEBUG --verbose up --build -d'."
	@echo "stop                   --- Run 'docker-compose kill/rm/prune'."
	@echo "stop-one               --- Run 'docker-compose kill <one>'."
	@echo "clean                  --- Remove all docker files and history."
	@echo "test                   --- Run 'npm run headless'."
	@echo "test-list              --- Show available polis tests"
	@echo "test-one one=<test>    --- 'cypress run --spec <polis-path>/<one> \#headless'

echo-one:
	@echo "one: ${one}"

restart:
	make stop
	make start

restart-one:
	make stop-one one=${one}; make start-one one=${one}

start:
	@echo "--- Running 'docker-compose up --build -d'..."
	GIT_HASH=`git log --pretty="%h" -n 1` ${SUDO} docker-compose up --build -d

start-one:
	@echo "--- Running 'docker-compose start --build -d ${one}'..."
	GIT_HASH=`git log --pretty="%h" -n 1` ${SUDO} docker-compose up -d ${one}
	${SUDO} docker-compose up -d

start-debug:
	@echo "--- Running 'docker-compose --log-level DEBUG --verbose up --build -d'..."
	GIT_HASH=`git log --pretty="%h" -n 1` ${SUDO} docker-compose --log-level DEBUG --verbose up --build -d

stop:
	@echo "--- Running 'docker-compose kill/rm/prune'..."
	${SUDO} docker-compose kill
	${SUDO} docker-compose rm -f
	${SUDO} docker system prune --volumes -f

stop-one:
	@echo "--- Running 'docker-compose stop/rm ${one}'..."
	${SUDO} docker-compose stop ${one}
	${SUDO} docker-compose rm -f ${one}
	${SUDO} docker images -a | grep polisdemo/${one} | awk '{print $3}' | xargs ${SUDO} docker rmi --no-prune

clean:
	@echo "--- Copy and past the following commands..."
	@echo 'docker rm -f $$(docker ps -aq)'
	@echo 'docker rmi -f $$(docker images -q)'
	@echo 'docker system prune --volumes -f'
	@echo 'echo done'

test:
	# change to 'npm run test' after merge with master
	@echo "--- Running 'npm run headless'"
	cd e2e; npm run headless

test-list:
	@echo "available polis e2e tests:"
	cd e2e/cypress/integration/polis; tree

test-one:
	@echo "--- running cypress e2e test: ${one}"
	cd e2e; ./node_modules/.bin/cypress run --headless --browser=chrome --spec './cypress/integration/polis/${one}'
	

APP = gen_ai

clean:
	docker ps -a | grep ${APP} | awk '{print $$1}' | xargs -r docker rm && docker rmi -f ${APP}

build: clean
	docker build -t ${APP} .

container:
	docker run -it --rm -p 7860:7860 -v $(shell pwd)/${APP}:/app/${APP} ${APP} bash

download_data:
	bash gen_ai/copy_resources.sh

publish:
	echo "Publishing the image to be discussed"
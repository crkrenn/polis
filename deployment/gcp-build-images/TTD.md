https://cloud.google.com/build/docs/build-push-docker-image

https://cloud.google.com/build/docs/interacting-with-dockerhub-images


        $ printf "s3cr3t" | gcloud secrets create my-secret --data-file=- \
            --replication-policy=user-managed \
            --locations=us-central1,us-east1
figure out build/env variables docker-compose and dockerfile
repeat 5 { sleep 1; date} | ts -s "%.S || %H:%M:%S ||"  
add timestamps to next build

add sed commands to makefile
 2786  sed -i"" -e "s/COPY polis.config.template.js/#COPY polis.config.template.js/" client-*/Dockerfile
 2789  sed -i "" -e "s/#COPY polis.config.template.js/COPY polis.config.template.js/" client-*/Dockerfile

fix Makefile so that mktemp is only called once 
consider fixing other redundant targets (do make clean first)

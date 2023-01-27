https://cloud.google.com/build/docs/build-push-docker-image

https://cloud.google.com/build/docs/interacting-with-dockerhub-images


        $ printf "s3cr3t" | gcloud secrets create my-secret --data-file=- \
            --replication-policy=user-managed \
            --locations=us-central1,us-east1
figure out build/env variables docker-compose and dockerfile

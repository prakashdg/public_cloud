FROM alpine:3.8

RUN apk update \
    && apk add --no-cache ansible bash build-base ca-certificates cdrkit \
    freetype-dev gdb git graphviz \
    python3-dev python3 


RUN python3 -m ensurepip && rm -r /usr/lib/python*/ensurepip \
    && pip3 --timeout 200 install --upgrade pipenv 

RUN ln -sf /usr/bin/pip3 /usr/bin/pip \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && ln -sf /usr/bin/pydoc3 /usr/bin/pydoc \
    && chmod a+s /bin/ping

RUN pip3 install --no-cache-dir azure-cli-core==2.5.1 azure-cli-nspkg==3.0.4 azure-cli-telemetry==1.0.4 azure-common==1.1.25 azure-core==1.5.0 azure-mgmt-compute==11.1.0 azure-mgmt-core==1.0.0 azure-mgmt-resource==9.0.0 azure-mgmt-storage==10.0.0 azure-nspkg==3.0.2 azure-storage-blob==2.1.0 azure-storage-common==2.1.0

ENTRYPOINT ["/bin/bash", "--login", "-s"]


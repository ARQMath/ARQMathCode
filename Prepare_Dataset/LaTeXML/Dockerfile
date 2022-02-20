FROM ubuntu:21.10

ENV DEBIAN_FRONTEND=noninteractive \
    TERM=xterm

RUN set -e -o xtrace \
  ; apt-get -qy update \
  ; apt-get -qy upgrade \
  ; apt-get -qy install --no-install-recommends latexml git python3.9 python3-pip \
  ; pip install tqdm git+https://github.com/MIR-MU/TangentCFT.git lxml~=4.5.0 beautifulsoup4~=4.8.2

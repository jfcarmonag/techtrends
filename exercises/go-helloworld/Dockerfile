FROM golang:alpine

ENV GO111MODULE off

WORKDIR /go/src/app

ADD . .

RUN go build  -o helloworld

EXPOSE 6111

CMD ["./helloworld"]
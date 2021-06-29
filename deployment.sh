#!/bin/bash
DEPLOYMENT_BUCKET="origin-1234"
STACK_NAME="husky-shelters-1"

while getopts ":bdp" OPTION; do
    case $OPTION in
    d)
      DEPLOY=1
      ;;
    p)
      PACKAGE=1
      ;;
    b)
      BUILD=1
      ;;
    *)
      ;;
    esac
done

if [[ $BUILD == 1 ]]
then
    pip3 install --target package -r requirements.txt
    cp -a src/. package/
    
fi


if [[ $BUILD == 1 ]]
then
  pip3 install --target package -r requirements.txt
  cp -a src/. package/
fi

if [[ $PACKAGE == 1 ]]
then
    aws cloudformation package --template-file template.yaml --s3-bucket $DEPLOYMENT_BUCKET --output-template-file packaged-template.json
fi

if [[ $DEPLOY == 1 ]]
then
    aws cloudformation deploy --template-file packaged-template.json --stack-name $STACK_NAME --capabilities CAPABILITY_NAMED_IAM
fi
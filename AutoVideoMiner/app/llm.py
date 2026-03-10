from __future__ import annotations

import os
from typing import Tuple

import boto3
from langchain_aws import BedrockEmbeddings, ChatBedrock

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def init_bedrock() -> Tuple[ChatBedrock, BedrockEmbeddings]:
    """Initialize shared Bedrock client, chat LLM and embedding model.

    Current unified defaults:
    - Chat: amazon.nova-lite-v1:0
    - Embedding: amazon.titan-embed-text-v1
    """
    aws_access_key = AWS_ACCESS_KEY
    aws_secret_key = AWS_SECRET_KEY
    aws_region = AWS_REGION

    if not aws_access_key or not aws_secret_key:
        raise RuntimeError("未检测到 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY 环境变量，请先设置。")

    boto3_client = boto3.client(
        "bedrock-runtime",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region,
    )

    embeddings = BedrockEmbeddings(
        client=boto3_client,
        model_id="amazon.titan-embed-text-v1",
        region_name=aws_region,
    )
    llm = ChatBedrock(
        client=boto3_client,
        model_id="amazon.nova-lite-v1:0",
        model_kwargs={"temperature": 0},
    )
    return llm, embeddings

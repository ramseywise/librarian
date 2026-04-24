---
title: Use Google ADK and MCP with an external server | Google Cloud Blog
url: https://cloud.google.com/blog/topics/developers-practitioners/use-google-adk-and-mcp-with-an-external-server
url_hash: 5e50e6e1
domain: cloud.google.com
date: 2026-04-24
tags: [web, reference]
summary: Captured from cloud.google.com on 2026-04-24
sources:
  - raw/web/2026-04-24-cloud-google-com-blog-topics-developers-practitioners-use-go-5e50e6e1.md
---

# Use Google ADK and MCP with an external server | Google Cloud Blog

> Source: https://cloud.google.com/blog/topics/developers-practitioners/use-google-adk-and-mcp-with-an-external-server

## A guide to Google ADK and MCP integration with an external server

Generative AI Field Solutions Architect

Build, scale, govern, and optimize agents

For AI-powered agents to perform useful, real-world tasks, they need to reliably access tools and up-to-the-minute information that lives outside the base model. Anthropic’s Model Context Protocol (MCP) is designed to address this, providing a standardized way for agents to retrieve that crucial, external context needed to inform their responses and actions.

This is vital for developers who need to build and deploy sophisticated agents that can leverage enterprise data or public tools. But integrating agents built with Google's Agent Development Kit (ADK) to communicate effectively with an MCP server, especially one hosted externally, might present some integration challenges.

Today, we’ll guide you through developing ADK agents that connect to external MCP servers, initially using Server-Sent Events (SSE). We’ll take an example of an ADK agent leveraging MCP to access Wikipedia articles, which is a common use case to retrieve external specialised data. We will also introduce Streamable HTTP, the next-generation transport protocol designed to succeed SSE for MCP communications.

Before we start, let's make sure we all understand the following terms:

SSE enables servers to push data to clients over a persistent HTTP connection. In a typical setup for MCP, this involved using two distinct endpoints: one for the client to send requests to the server (usually via HTTP POST) and a separate endpoint where the client would establish an SSE connection (HTTP GET) to receive streaming responses and server-initiated messages.

SSE enables servers to push data to clients over a persistent HTTP connection. In a typical setup for MCP, this involved using two distinct endpoints: one for the client to send requests to the server (usually via HTTP POST) and a separate endpoint where the client would establish an SSE connection (HTTP GET) to receive streaming responses and server-initiated messages.

MCP is an open standard designed to standardize how Large Language Models (LLMs) interact with external data sources, APIs and resources as agent tools, MCP aims to replace the current landscape of fragmented, custom integrations with a universal, standardized framework.

MCP is an open standard designed to standardize how Large Language Models (LLMs) interact with external data sources, APIs and resources as agent tools, MCP aims to replace the current landscape of fragmented, custom integrations with a universal, standardized framework.

Streamable HTTP utilizes a single HTTP endpoint for both sending requests from the client to the server, and receiving responses and notifications from the server to the client.

Streamable HTTP utilizes a single HTTP endpoint for both sending requests from the client to the server, and receiving responses and notifications from the server to the client.

## Step 1: Create an MCP server

You need the following python packages installed in your virtual environment before proceeding. We will be using the uv tool in this blog.

Here’s an explanation of the Python code server.py :

It creates an instance of an MCP server using FastMCP

It creates an instance of an MCP server using FastMCP

It defines a tool called extract_wikipedia_article decorated with @mcp.tool

It defines a tool called extract_wikipedia_article decorated with @mcp.tool

It configures an SSE transport mechanism SseServerTransport to enable real-time communication, typically for the MCP server interactions.

It configures an SSE transport mechanism SseServerTransport to enable real-time communication, typically for the MCP server interactions.

It creates a web application instance using the Starlette framework and defines two routes, message and sse .

It creates a web application instance using the Starlette framework and defines two routes, message and sse .

You can read more about SSE transport protocol here .

You can read more about SSE transport protocol here .

To start the server, you can run the command uv run server.py .

Bonus tip, to debug the server using MCP Inspector , execute the command uv run mcp dev server.py .

## Step 2: Attach the MCP server while creating ADK agents

The following explains the Python code in the file agent.py :

Uses MCPToolset.from_server with SseServerParams to establish a SSE connection to a URI endpoint. For this demo we will use http://localhost:8001/sse , but in production this would be a remote server.

Uses MCPToolset.from_server with SseServerParams to establish a SSE connection to a URI endpoint. For this demo we will use http://localhost:8001/sse , but in production this would be a remote server.

Create an ADK Agent and call get_tools_async to get the tools from the MCP server.

Create an ADK Agent and call get_tools_async to get the tools from the MCP server.

## Step 3: Test your agent

We will use the ADK developer tool to test the agent.

Create the following directory structure:

The content for __init__.py and .env are as follows:

Start the UI with the following command:

This will open up the ADK developer tool interface as shown below:

It is worth noting that in March 2025, MCP released a new transport protocol called Streamable HTTP . The Streamable HTTP transport allows a server to function as an independent process managing multiple client connections via HTTP POST and GET requests. Servers can optionally implement Server-Sent Events (SSE) for streaming multiple messages, enabling support for basic MCP servers as well as more advanced servers with streaming and server-initiated communication.

The following code demonstrates how to implement a Streamable HTTP server, where the tool extract_wikipedia_article will return a dummy string to simplify the code.

You can start the Streamable HTTP MCP server using by running the following:

To debug with MCP Inspector , select Streamable HTTP and fill in the MCP Server URL http://localhost:3000/mcp .

For production deployments of MCP servers, robust authentication is a critical security consideration. As this field is under active development at the time of writing, we recommend referring to the MCP specification on Authentication for more information.

For an enterprise grade API governance system which, similar to MCP, can generate agent tools:

Apigee centralizes and manages any APIs, with full control, versioning, and governance

Apigee centralizes and manages any APIs, with full control, versioning, and governance

API Hub organizes metadata for any API and documentation

API Hub organizes metadata for any API and documentation

Application Integrations support many existing API connections with user access control support

Application Integrations support many existing API connections with user access control support

ADK supports these Google Cloud Managed Tools with about the same number of lines of code

ADK supports these Google Cloud Managed Tools with about the same number of lines of code

To get started today, read the documentation for ADK. You can create your own Agent with access to available MCP servers in the open community with ADK.

Developers & Practitioners

AI & Machine Learning

## Next '26 Hands-On: 10 Codelabs to Build Featured Tech

By Mandy Grover • 3-minute read

## Level Up Your Agents: Announcing Google's Official Skills Repository

By Megan O'Keefe • 2-minute read

## What’s new with the Cross-Cloud Network at Next ‘26

By Rob Enns • 13-minute read

## Introducing Gemini Enterprise Agent Platform, powering the next wave of agents

By Michael Gerstenhaber • 12-minute read

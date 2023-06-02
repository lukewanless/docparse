# Docparse
 Welcome to Docparse, this is a project designed for efficiently parsing custom docx templates for organisations and using LLM's to generate realistic replacement text without breaking formatting. 

## Table of Contents
- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contact](#contact)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

Here are some things you'll need to have before you start:

- A computer running macOS or Linux
- An installed version of Python 3.10.8 or later
- An Open AI API key 

### Installation

1. Clone the repo
2. Install the dependencies listed in [requirements](requirements.txt)
3. To set the OpenAI api key as an environmental variable add `export OPENAI_KEY="YOUR_KEY"` to your bashrc (Linux) or zshrc (MacOS).

## Usage 

1. To run the project on localhost first activate your python environment with installed dependencies and navigate to the app subdirectory and run the following:

![Demo](https://user-images.githubusercontent.com/49578317/242752124-d7e88987-2e29-401d-b5c1-52f22b76d3ae.gif)

2. Create or use an existing .docx file such as the one shown below.

![Original](https://user-images.githubusercontent.com/49578317/242757447-eb9bbbdd-44a7-4f30-a3d1-1a75a5a5f43e.gif)

3.  Navigate to the localhost port running the application (usually 127.0.0.1:8000), upload the file then click "Parse Document". 

![upload](https://user-images.githubusercontent.com/49578317/242757057-b5bf1650-9939-489e-abd1-cfdbad466e33.gif)


4.  You will then be taken to the document editor whereby you can edit a topic to steer the generation of replacement content. Each section of the document will be parsed and classified. You can toggle this classication if it is inaccurate then click "Regenerate" to generate replacement text for each section. 

![generate_content](https://user-images.githubusercontent.com/49578317/242757151-eda38bcc-113a-443a-879a-ccf6d305bad6.gif)

5.  Hyperlinks, emails, dates, full names and more are supported text types. For links and emails the document text will be changed however the redirect link will remain unchanged to support counter-deception. 

![links_emails](https://user-images.githubusercontent.com/49578317/242757245-aa41c27e-d0c8-49c8-baff-e785ca3bc842.gif)

6. Finally save and download the document. The text will be replaced whilst retaining formating and any unchanged text. 

![save_doc](https://user-images.githubusercontent.com/49578317/242757373-489894b8-84fd-45e4-adac-7bbc58e3e6d8.gif)


## Contact 
luke@wanlessco.com.au 

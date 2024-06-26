# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click
from devai.util.file_processor import format_files_as_string
from vertexai.generative_models import (
    GenerativeModel,
    Image,
)
from google.cloud.aiplatform import telemetry
import os
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound, PermissionDenied
from google.api_core.gapic_v1.client_info import ClientInfo
import logging


USER_AGENT = 'cloud-solutions/genai-for-developers-v1.0'
model_name="gemini-1.5-pro"

def ensure_env_variable(var_name):
    """Ensure an environment variable is set."""
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    return value

def get_prompt( secret_id: str) -> str:
    """Retrieves a secret value from Google Secret Manager.

    Args:
        secret_id: The ID of the secret to retrieve.

    Returns:
        The secret value as a string, or None if the secret is not found or the user lacks permission.
    """    
    try:
        project_id = ensure_env_variable('PROJECT_ID')
        logging.info("PROJECT_ID:", project_id)

        client = secretmanager.SecretManagerServiceClient(
        client_info=ClientInfo(user_agent=USER_AGENT)
        )
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        try:
            response = client.access_secret_version(name=name)
            payload = response.payload.data.decode("utf-8")
            logging.info(f"Successfully retrieved secret ID: {secret_id} in project {project_id}")
            return payload
        
        except PermissionDenied:
            logging.warning(f"Insufficient permissions to access secret {secret_id} in project {project_id}")
            return None
        
        except NotFound:
            logging.info(f"Secret ID not found: {secret_id} in project {project_id}")
            return None
        
        except Exception as e:  # Catching a broader range of potential errors
            logging.error(f"An unexpected error occurred while retrieving secret '{secret_id}': {e}")
            return None
    
    except EnvironmentError as e:
        logging.error(e)

@click.command(name='readme')
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def readme(context):
    """Create a README based on the context passed!
    
    This is useful when no existing README files exist. If you already have a README `update-readme` may be a better option.
    
    """
    click.echo('Generating and printing the README....')
    

    source='''
            ### Context (code) ###
            {}

            '''
    qry = get_prompt('document_readme')

    if qry is None:
        qry='''
            ### Instruction ###
            Generate a comprehensive README.md file for the provided context. The README should follow industry best practices and be suitable for professional developers. Resources like dora.dev, stc.org, and writethedocs.org should be used as guidelines.

            It should be clear, concise, and easy to read written in a professional mannor conveying the project's purpose and value effectively.
           
            ### Output Format ### 
            A well-structured README.md file in Markdown format. The README, using markdown formatting,  should include the following sections (at a minimum):

            Description
            Table of Contents
            Features
            Installation
            Usage
            Contributing
            License
            Contact

            ### Example Dialogue ###
            Instruction:
            Generate a comprehensive README.md file for the provided project. The README should follow industry best practices and be suitable for professional developers.

            Context (project):
            Project Name: Cymbal Coffee
            Description: A Python library for data analysis and visualization, designed to simplify common data wrangling tasks and generate insightful plots.
            Technologies Used: Python, Pandas, NumPy, Matplotlib, Seaborn
            Features:
            * Easy data loading from various sources (CSV, Excel, SQL, etc.)
            * Powerful data cleaning and transformation functions
            * Interactive data exploration with summary statistics and filtering
            * Customizable visualization templates for common plot types
            * Integration with Jupyter Notebooks for seamless analysis
            Installation: pip install cymbal
            Usage: See examples in the 'examples' directory or visit our documentation: [link to documentation]
            Contribution Guidelines: We welcome contributions! Please follow our style guide and submit pull requests for review.
            License: Apache 2.0 License
            Contact Information: Email us at support@cymbal.coffee or open an issue on our GitHub repository.
            '''

    # Load files as text into source variable
    source=source.format(format_files_as_string(context))

    code_chat_model = GenerativeModel(model_name)
    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = code_chat_model.start_chat()
        code_chat.send_message(qry)
        response = code_chat.send_message(source)

    click.echo(f"{response.text}")

@click.command(name='update-readme')
@click.option('-f', '--file', type=str, help="The existing release notes to be updated.")
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def update_readme(context):
    """Ureate a release notes based on the context passed!
    
    
    
    
    """
    click.echo('Update README')



@click.command(name='releasenotes')
# @click.option('-v', '--version', type=str, help="The version number for the release notes.")
# @click.option('-f', '--file', type=str, help="The existing release notes to be updated.")
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def releasenotes(context):
    """Create a release notes based on the context passed!
    
    
    
    
    """
    
    click.echo('Generating and printing release notes.')
    

    source='''
            ### Context (code) ###
            {}

            '''
    qry = get_prompt('document_readme')

    if qry is None:
        qry='''
            ### Instruction ###
           Create detailed release notes
            '''

    # Load files as text into source variable
    source=source.format(format_files_as_string(context))

    code_chat_model = GenerativeModel(model_name)
    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = code_chat_model.start_chat()
        code_chat.send_message(qry)
        response = code_chat.send_message(source)

    click.echo(f"{response.text}")


@click.command(name='update-releasenotes')
@click.option('-v', '--version', type=str, help="The version number for the release notes.")
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def update_releasenotes(context):
    """Update release notes based on the context passed!
    
    
    
    
    """
    click.echo('create release notes')


@click.group()
def document():
    """
    Generate documentation for your project usnig GenAI.
    """
    pass

document.add_command(readme)
document.add_command(update_readme)
document.add_command(releasenotes)
document.add_command(update_releasenotes)
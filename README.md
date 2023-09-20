# Meltano documentaion

Welcome to Meltano documentaion! This guide navigates the use of Meltano as indented by this project.

Wherever our approach diverges from the suggestions in the [official Meltano documentation](https://docs.meltano.com), we will emphasize the difference and provide our rationale.

Although Meltano offers features for constructing an entire data pipeline, from extraction to data transformation and orchestration, we tend to favor other tools that handle some of these tasks more efficiently, such as dbt and Airflow. Hence, we primarily use Meltano for [data integration](https://docs.meltano.com/getting-started/part2#run-your-data-integration-el-pipeline) (extract and load), barring certain specific cases where we state otherwise.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## Get started fast

In order to be able to run anything, you will need to
* Install the current python packages from requirements.txt
* Set any anvironment variables required by the extractors or loaders. As of now, the following env variables are needed:

- AWS_ID - User ID for access to AWS S3 bucket (used the S3 loader)
- AWS_PSW - User password for access to AWS S3 bucket (used the S3 loader)
- CVENT_OAUTH_KEY - OAUTH key for authentication in the Cvent REST API (used by our custom extractor)
- TARGET_SNOWFLAKE_PASSWORD - password of the "DBT" user in snowflake (used by the final loader)

After that you can run `meltano run <extractor_name> <loader_name>` to run any of the implemented workflows. You may check what is currently implemented in the "pipelines/pipeline_config.yml" file. Look for the "name" parameter.

In order to get a better understanding of the project and to know how to add more extractors/loaders, you may follow the sections below.

## Table of Contents

1. [Recipes](#1-recipes)
2. [Project Structure](#2-project-structure)
    1. [meltano.yml](#21-meltanoyml)
    2. [requirements.txt](#22-requirementstxt)
    3. [envs_config.yml](#23-envs_configyml)
    4. [plugins](#24-plugins)
        1. [extractors](#241-extractors)
        2. [loaders](#242-loaders)
        3. [mappers](#243-mappers)
    5. [pipelines](#25-pipelines)
3. [Custom Extractors](#3-custom-extractors)
    1. [Creating Custom Extractors](#31-creating-custom-extractors)
        1. [Create a Project Using the Cookiecutter Template](#311-create-a-project-using-the-cookiecutter-template)
        2. [Configure the Custom Extractor to Consume Data from the Source](#312-configure-the-custom-extractor-to-consume-data-from-the-source)
        3. [Test the Newly Created Tap](#313-test-the-newly-created-tap)
    2. [Incremental Replication Implementation](#32-incremental-replication-implementation)
        1. [Filter Mechanism in Request's URL](#321-filter-mechanism-in-requests-url)
        2. [Filter Mechanism in Request's URL](#322-filter-mechanism-in-requests-body)
        3. [No API Filtering Mechanism](#323-no-api-filtering-mechanism)
    3. [Parent-Child Streams](#33-parent-child-streams)

## 1. Recipes

There is small differences between the "Getting Started" instructions in the meltano documentation and how we suggest to do work. The main difference is the folder structure. In the "Getting Started" Meltano documentation, you use CLI commands that fills the configurations for extractor and loaders in the main project file, "meltano.yml".

Then you simply run `meltano run <exractor_name> <loader_name>` and meltano knows what to do.

Here, we choose to sepparate the configurations for extractors, loaders and enviroments in different YAML files inside their respective folder, and then in the "meltano.yml" we just use the "include_paths" configuration to import each one of those files into the main YAML. This is indended to keep things modular, organized and to avoid having a gigantic and hard-to-read "meltano.yml" file as the project grows.

You can still use the CLI commands to get the configuration for the plugins that you want and they will show up in the "meltano.yml". In order to follow this frameworks simply paste the new block of code that showed up in "meltano.yml" into one of the plugin-specific YAML files.

Also, instead of using the CLI you can choose to add the configurations into it's respective YAML manually, following the documentation for each plugin or by copying and pasting from somewhere else. When you are done, run "meltano install" to install the plugins you just added and then use "meltano run" in the same way.

[TBD]

## 2. Project Structure

A Meltano project is a directory on your filesystem containing text-based files. This arrangement allows you to employ DataOps best practices, such as version control, code review, and continuous integration and deployment (CI/CD), as you would in any other software development project.

*Note: The [official Meltano documentation](https://docs.meltano.com/concepts/project) advises using the `meltano init` command to initiate a project. However, this leads to a complex project structure that doesn't align with our purpose for using Meltano just for extraction and load.*

This project have the following file tree:

``` bash
    ./
    ├── bitbucket-pipelines.yml
    ├── create_custom.sh
    ├── Dockerfile
    ├── DOCS.md
    ├── envs_config.yml
    ├── meltano.yml
    ├── pipelines/
    │   └── example_pipeline/
    │       └── example_config.yml
    ├── plugins/
    │   ├── custom/
    │   │   └── custom_config.yml
    │   ├── extractors/
    │   │   └── extractors_config.yml
    │   ├── loaders/
    │   │   └── loaders_config.yml
    │   └── mappers/
    │       └── mappers_config.yml
    ├── README.md
    ├── requirements.txt
```

### 2.1. `meltano.yml`

Every Meltano project requires a `meltano.yml` file. This file holds your project configuration and signifies to Meltano that a specific directory is a Meltano project. The`version` is the only obligatory property, which should always be `1`.

*Note: The official Meltano documentation recommends using the Meltano CLI to configure the entire Meltano project and run pipelines, resulting in a large `meltano.yml` configuration file, making it challenging to locate a specific configuration for modification. As stated in section 1, we utilize the `include_paths` directive to foster a more modular and intuitive setup for managing distinct parts of the project configuration.*

A crucial configuration for Meltano projects is the  `state_backend`, which determines where your pipeline states for incremental replication will be stored and retrieved by Meltano.

By default, the files will be stored and handled inside the `.meltano` directory. However, you might want to store these states in a cloud environment for your production pipelines. To achieve this, you should keep uncommented the `state_backend` block of code on the `meltano.yml` file.

For instance, if you are using an S3 bucket, your `meltano.yml` should look like this:

``` yaml
# meltano.yml
version: 1
include_paths:
  - envs_config.yml
  - ./pipelines/**/*.yml
  - ./plugins/custom/custom_config.yml
  - ./plugins/extractors/extractors_config.yml
  - ./plugins/loaders/loaders_config.yml
  - ./plugins/mappers/mappers_config.yml
state_backend:
  uri: s3://<bucket-name>/<prefix for state JSON blobs>
  s3:
    aws_access_key_id: ${AWS_KEY_ID_STATE_BACKEND}
    aws_secret_access_key: ${AWS_SECRET_STATE_BACKEND}
```

Currently, for this project we are using the state backend pointing to the "meltano-lake" bucket on AWS

### 2.2. `requirements.txt`

This file will contain the appropriate extra necessary to set up the cloud state backend. For instance, taking into account the above example of an S3 state backend, you would have:

``` text
# requirements.txt
meltano[s3]
```

### 2.3. `envs_config.yml`

In this file, we define Meltano environments to run our pipelines. The main use of these environments is to define environment variables that will be accessed by the plugins in a pipeline at runtime.

That is, here is the place where you set parameters such as passwords and target schema/database for separation between development and production. By default, when you run "meltano run" it will read the variables in the dev section.

The following example illustrates a case where we can change the output database and state backend by simply passing a different environment when running pipelines.

The `default_environment` property defines which environment will be passed to pipelines in case the user does not specify one.

``` yaml
default_environment: dev      
environments:
  # Creation of environments
  - name: dev
    # 'env' indentation receives variables to export to meltano pipelines
    env:
      #To Use environment variables coming from .env or another source use
      OUT_DB_USER: ${DEV_DB_USER}
      OUT_DB_PASSWORD: ${DEV_DB_PASSWORD}
      OUT_DB_NAME: ${DEV_DB_NAME}
      #For Azure State Backend
      AZURE_CONN_STATE_BACKEND: ${AZURE_CONNECTION_STRING_STATE_BACKEND_DEV}

  - name: prod
    env:
      #Place your 'prod' variables here
      OUT_DB_USER: ${PROD_DB_USER}
      DB_PASSWORD: ${PROD_DB_PASSWORD}
      OUT_DB_NAME: ${PROD_DB_NAME}
      #For Azure State Backend
      AZURE_CONN_STATE_BACKEND: ${AZURE_CONNECTION_STRING_STATE_BACKEND_PROD}
```

### 2.4. `plugins/`

This directory contains the base building blocks of our data integration pipelines: plugins.

We separate each category into its folder: `extractors` (or taps), `loaders` (or targets), and `mappers` (inline data transformers) and `custom`. The first two will store the YAML files and configuration for built-in plugins that you can use by simply writing their name and passing its configuration, and meltano will know what to do. On mappers` you can add an additional step in the extraction to filter or transform data, and this is usually not used.

The `custom` folder contain extractor/loader plugins that were created by the user itself. The most common case for us will be [custom extractors](#3-custom-extractors) for different APIs.

#### 2.4.1. `extractors/`

Here we define the base plugins that will extract data from sources and set them in a stream for being redirected to a target.

Here is an example of a base extractor plugin definition:

``` yaml
# ./plugins/extractors/extractors_config.yml
plugins:
  extractors:
  - name: tap-postgres
    variant: meltanolabs
    pip_url: pipelinewise-tap-postgres
    config:
      host: ${VAR_IN_DB_HOST}
      user: ${VAR_IN_DB_USER}
      password: ${VAR_IN_DB_PASSWORD}
      dbname: ${VAR_IN_DB_NAME}
      default_replication_method: FULL_TABLE
```

As you can see, we simpliy write ther name of the extraction and it's respective configuration, and meltano knows what to do. You can explore all the available built-in extractors here: https://hub.meltano.com/extractors/

#### 2.4.2. `loaders/`

This kind of plugin will direct the data in the streams to a target destination.

Here is an example of a base loader plugin definition:

``` yaml
# ./plugins/loaders/loaders_config.yml
plugins:
  loaders:
  - name: target-postgres
    variant: transferwise
    pip_url: pipelinewise-target-postgres
    config:
      host: ${VAR_OUT_DB_HOST}
      user: ${VAR_OUT_DB_USER}
      password: ${VAR_OUT_DB_PASSWORD}
      dbname: ${VAR_OUT_DB_NAME}
      default_target_schema: public
      hard_delete: true

  - name: target-jsonl
    variant: andyh1203
    pip_url: target-jsonl
  - name: target-s3
    variant: crowemi
    pip_url: git+https://github.com/crowemi/target-s3.git
```

Same as before, we simpliy write ther name of the loader and it's respective configuration,. You can explore all the available built-in loaders here: https://hub.meltano.com/loaders/

#### 2.4.3. `mappers/`

ongoing

### 2.5. `pipelines/`

This is comething that we did not mention before. Other than running "meltano run <extractor_name> <loader_name>" you can create a "pipeline", that represents a configuration for a extractor-loader pair. By doing that you can run "meltano run <job_name>" instead to perform the extraction.

This folder is where those pipelines should defined. In the "pipeline_config.yml" file you can pull the existing extractors, loaders using the `inherit_from` parameter, add some more configuration and then create a `job`, which essentially is an alias (or `name`) for a sequence of `tasks`. Each task represents an extractor/load pair

As previously stated, we customize each plugin for use in a pipeline with an `inherit_from` directive. As the name suggests, plugins defined this way inherit all configurations from the base objects in the `plugins` folder and have additional configurations for the specific pipeline we are defining.

Here is an example that illustrates all these concepts:

``` yaml
plugins:
  extractors:
  - name: tap-postgres--orders
    inherit_from: tap-postgres
    config:
      port: ${VAR_IN_DB_PORT}
    select:
    - public-orders.*

  loaders:
  - name: target-postgres--orders
    inherit_from: target-postgres
    config:
      port: ${VAR_OUT_DB_PORT}

jobs:
- name: orders-pipeline
  tasks:
  - tap-postgres--orders target-postgres--orders
```

In this example, the base tap-postgres in the `plugins` folder extracts data from all tables of the `public` schema to put in a stream. However, after the `inherit_from` clause and the configuration `select`, only the `orders` table is streamlined in the `orders-pipeline` job (smart, hum?).

Once we have defined a pipeline (such as the `orders-pipeline` from the previous example), we can execute it via:

``` bash
# using the default environment
meltano run orders-pipeline

# or

# using a predefined environment in envs_config.yml, e.g. 'prod'

# meltano --environment=prod run  orders-pipeline
```

For the sake of completeness, let us comment on the purpose of the remaining files present in the base project structure:

- `cd_pipelines.yml`: skeleton CI/CD pipeline that you might be interested to build upon for your production setup;

- `Dockerfile`: basic setup for building a Meltano image with all plugins and pipelines from your project to be used in production, e.g. in a `DockerOperator` in Airflow.

- `.gitignore`, `.dockerignore`: pre-defined files you might want to ignore for use in the respective tools.

- `create_custom.sh`: simple bash script that helps in the workflow of developing [custom-extractors](#3-custom-extractors).

## 3. Custom Extractors

Custom extractors are tools or scripts developed to retrieve data from non-standard data sources like custom databases or SaaS APIs, such as Appwrite. They convert this data into a suitable format for loading into a target destination, such as a data warehouse. These extractors, known as taps in the Singer framework, do not come as integral parts of the tool in use.

Singer taps and targets can streamline the use of custom extractors. Singer, a popular data extraction tool, offers specifications for creating extractors and loaders. In Singer's context, a custom extractor is a tap tailored to meet an organization's specific requirements.

Operating taps and targets manually can be labor-intensive. Meltano extractor/loader plugins offer a more efficient approach. Meltano's EL (Extract and Load) capabilities manage the complexities of configuration, stream discovery, and state management associated with Singer.

### 3.1. Creating Custom Extractors

The following steps outline how to create a custom extractor for a Meltano project:

#### 3.1.1. Create a Project Using the Cookiecutter Template

Run the following commands at the root of your Meltano project:

``` bash
chmod +x create_custom.sh
bash create_custom.sh
```

These commands will prompt you to set up your project.

As a result, a new directory, tap-<source_name>, will appear in plugins/custom, containing the foundational code for your tap development, along with a `meltano.yml` file that you can use to test your custom extractor.

*Note: The `meltano.yml` file within the tap folder informs Meltano that the folder is also a Meltano project. This setup lets you test your plugin in isolation, without impacting your original Meltano project. Once your plugin behaves as expected, you can shift the directory back to the project root and use your new plugin as discussed earlier.*

Inside the tap folder, the main files we will be using in the development of the custom extractor are:

- `tap.py`: defines the basic tap configurations and the streams it will create when interacting with the data source;

- `client.py`: defines the basic stream class and objects necessary for interaction with the source system, like authentication, pagination, and base stream objects.

- `streams.py`: implements the stream objects to be returned by the tap by adapting the base objects in `client.py` for each API endpoint.

#### 3.1.2. Configure the Custom Extractor to Consume Data from the Source

This step involves adapting the extractor to access data from the preferred source.

While the specific implementation details can vary significantly depending on the API, the following steps are generally common across all implementations:

- Define tap configurations: In the `tap.py` file, you define your `Tap<source_name>` class. The `config_jsonschema` property of this object outlines the configuration parameters you will provide for your tap. Remember, this definition of tap configurations happens "in a vacuum", meaning you should provide these configurations for the tap to run in isolation.

*Note: When integrating with Meltano, you should define these same configurations in the `settings` property of the base plugin description. Keep in mind that Meltano won't be aware of the configurations you define at the `tap.py` level unless you specify them in the `settings` property of the plugin.*

- Identify the streams you need to replicate: In the Tap class, you need to implement the `discover_streams` method by returning a list of streams you want to extract data from.

The following example illustrates how to implement this:

``` python
# ./plugins/custom/tap_okta/tap.py
"""okta tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_okta import streams


class Tapokta(Tap):
    """okta tap class."""

    name = "tap-okta"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "okta_domain",
            th.StringType,
            required=True,
            description="Organization's unique subdomain in okta.",
        ),
        th.Property(
            "performance_optimization",
            th.BooleanType,
            description="Complex DelAuth configurations may degrade performance when fetching specific parts of the response, and passing this parameter can omit these parts, bypassing the bottleneck.",
        ),
        th.Property(
            "search",
            th.StringType,
            description="Searches for users with a supported filtering expression for most properties. Okta recommends this option for optimal performance.",
            examples=[
                'status eq "STAGED"',
                "lastUpdated gt \"yyyy-MM-dd'T'HH:mm:ss.SSSZ\"",
                'id eq "00u1ero7vZFVEIYLWPBN"',
                'type.id eq "otyfnjfba4ye7pgjB0g4"',
                'profile.department eq "Engineering"',
                'profile.occupation eq "Leader"',
                'profile.lastName sw "Smi"',
            ],
        ),
        th.Property(
            "limit",
            th.IntegerType,
            description="Specifies the number of results returned (maximum 200). If you don't specify a value for limit, the maximum (200) is used as a default.",
        ),
        th.Property(
            "sortBy",
            th.StringType,
            description="Specifies field to sort by (for search queries only).",
        ),
        th.Property(
            "sortOrder",
            th.StringType(allowed_values=["asc", "desc"]),
            description="Specifies sort order asc or desc (for search queries only). Sorting is done in ASCII sort order (that is, by ASCII character value), but isn't case sensitive. sortOrder is ignored if sortBy is not present, is optional and defaults to ascending.",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.oktaStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.UsersStream(self),
        ]


if __name__ == "__main__":
    Tapokta.cli()
```

- Specify the base API URL: This is the `url_base` property of the `<source_name>Stream` class in the `client.py` file.

``` python
# ./plugins/custom/tap_okta/client.py

# ... 

class oktaStream(RESTStream):
    """okta stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        # TODO: hardcode a value here, or retrieve it from self.config
        return f"https://{self.config.get('okta_domain')}"

# ...

```

- Outline the streams' schemas: You should define the streams you intend to use in the `streams.py` file. Pay particular attention to the `path` property. This gets appended to the base URL to determine the streams' endpoint in the API. Define the stream's schema as well. While you can do this directly within the class (similar to the `config_jsonschema` property of the tap's class), we recommend setting the `schema_filepath` and creating a `schemas` folder within the tap directory to store the schema files.

``` python
# ./plugins/custom/tap_okta/streams.py

# ...

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
  
class UsersStream(oktaStream):
    """Define custom stream."""

    name = "users"
    path = "/api/v1/users"
   
    schema_filepath = SCHEMAS_DIR / "events.json" 

# ...

```

Please note, by default, RESTStreams presume the REST method is `GET`. Typically, you set up the `get_url_params` method to adapt the endpoint for querying purposes. However, if the API uses a `POST` method, you should set your stream's `rest_method` attribute to `POST` and overwrite the `prepare_request_payload` method.

``` python
# ./plugins/custom/tap_totango/streams.py

# ...

class UsersStream(totangoStream):
    """Define custom stream."""

    name = "users"
    rest_method = "POST"

    path = "/api/v1/search/users"

    schema_filepath = SCHEMAS_DIR / "users.json"

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        params = self.config
        query = {
            "terms": params["users_terms"],
            "fields": params["users_fields"],
            "offset": params["users_offset"],
            "count": params["users_count"],
            "sort_by": params["users_sort_by"],
            "sort_order": params["users_sort_order"],
        }
        data = {"query": json.dumps(query)}
        return data

# ...

```

#### 3.1.3. Test The Newly Created Tap

Navigate to the tap folder and configure your plugins' `settings` to match the ones you defined. Next, run `meltano install`.

 After that, run `meltano run tap-<source_name> target-jsonl` and check the result in the `output` folder that will be created.

### 3.2. Incremental Replication Implementation

Incremental replication is a vital feature in data integration pipelines. It optimizes the extraction time and resource usage by only extracting modified data. The Meltano SDK offers incremental replication mechanisms for three types of implementation, based on the API's filtering capabilities.

Remember, for users familiar with the Singer specification, we're aware of the "at least once" method for incremental extractions. Nonetheless, we deliberately implement incremental extractions using a "greater than" comparison, believing the benefits of eliminating duplicate data outweigh the potential downsides.

*Note [for users familiar with the Singer spec]: we are aware of the [at least once](https://sdk.meltano.com/en/latest/implementation/at_least_once.html) method for incremental extractions. Nonetheless, we deliberately implement incremental extractions using a "greater than" comparison, believing the benefits of eliminating duplicate data outweigh the potential downsides.*

#### 3.2.1. Filter Mechanism in Request's URL

If the API offer filtering capabilities as query parameters in the URL (which most APIs of practical interest do), you can take advantage and request the incremental records directly at the source by overwriting the `get_url_params` method, as the following example demonstrates:

``` python
# ./plugins/custom/tap_okta/streams.py

# ...

class UsersStream(oktaStream):

# ...

    def get_url_params(
        self, context: dict | None, next_page_url: str | None
    ) -> dict[str, Any]:
        
        # ...

        if self.replication_method == "INCREMENTAL":
            bookmark = self.get_starting_timestamp(context)
            if bookmark:
                # convert date to expected format for querying the API
                bookmark_date = str(bookmark).split("+")[0] + ".000Z"

                url_params["search"] = f'{self.replication_key} gt "{bookmark_date}"'
        
        # ...

# ...
```

#### 3.2.2. Filter Mechanism in Request's Body

This is analogous to the previous implementation but for streams that have a `POST`  rest method. Once again, we can take advantage and request the incremental records directly at the source, but this time overwriting the `prepare_request_payload` method, as in the following example:

``` python
# ./plugins/custom/tap_totango/streams.py

# ...

class EventsStream(totangoStream):

# ...

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002
    ) -> dict | None:
        # ...

        if self.replication_method == "INCREMENTAL":
            bookmark = self.get_starting_replication_key_value(context)
            if bookmark:
                # in this case, the date value is a timestamp in Unix time (EPOCH) milliseconds format.
                payload["terms"] = [
                    {
                        "type": "date", 
                        "term": {self.replication_key}, 
                        "gte": {bookmark},
                                    
                    },
                ]

        
        # ...
        
        # ...

# ...
```

#### 3.2.3. No API Filtering Mechanism

If the API doesn't provide a filtering mechanism, request the complete object collection and parse the response to only stream the incremental records. You can accomplish this within the `parse_response` method. Overwriting the `request_records` method is necessary to provide the `context` dictionary to the `parse_response` method, thereby giving it access to the tap's state.

``` python
def parse_response(
        self, response: Response, context: dict | None
    ) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: A raw `requests.Response`_ object.

        Yields:
            One item for every item found in the response.

        .. _requests.Response:
            https://requests.readthedocs.io/en/latest/api/#requests.Response
        """
        records = response.json()
        bookmark = self.get_bookmark(context)
        if self.replication_method == "INCREMENTAL" and bookmark:
            incremental_records = []
            for record in records:
                if self.check_incremental(record, bookmark):
                    incremental_records.append(record)
            yield from incremental_records
        else:
            yield from extract_jsonpath(self.records_jsonpath, input=records)

    def request_records(self, context: dict | None) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.

        If pagination is detected, pages will be recursed automatically.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            An item for every record in the response.
        """
        paginator = self.get_new_paginator()
        decorated_request = self.request_decorator(self._request)

        with metrics.http_request_counter(self.name, self.path) as request_counter:
            request_counter.context = context

            while not paginator.finished:
                prepared_request = self.prepare_request(
                    context,
                    next_page_token=paginator.current_value,
                )
                resp = decorated_request(prepared_request, context)
                request_counter.increment()
                self.update_sync_costs(prepared_request, resp, context)
                yield from self.parse_response(resp, context)

                paginator.advance(resp)
```

### 3.3. Parent-Child Streams

The Tap SDK supports parent-child streams, by which one stream type can be declared to be a parent to another stream, and the child stream will automatically receive `context` from a parent record each time the child stream is invoked.

We recommend the following approach to set up this stream configuration:

- Set `parent_stream_type` in the child-stream’s class to the class of the parent.

- Override the `get_child_context` method to return a new child context object based on records and any existing context from the parent stream.

- Use values from the parent context using the `{<context_key>}` syntax.

Here is an abbreviated example that uses the above techniques. In this example, EventsStream is a child of AccountsStream.

``` python
# ./plugins/custom/tap_totango/streams.py

# ...

class AccountsStream(totangoStream):
    """Define custom stream."""

    name = "accounts"
    
    # ...

    def get_child_context(self, record: dict, context: t.Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "account_id": record["name"],
        }
    
    # ...

# ...

class EventsStream(totangoStream):
    """Define custom stream."""

    name = "events"
    
    # ...

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002
    ) -> dict | None:
        
        # ...

        data["account_id"] = "{account_id}"
        
        # ...

# ...
```

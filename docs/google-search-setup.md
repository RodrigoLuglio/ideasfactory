# Setting Up Google Custom Search API

This guide will walk you through setting up the Google Custom Search API for the IdeasFactory Project Manager agent.

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a name for your project and click "Create"
5. Wait for the project to be created, then select it from the dropdown

## Step 2: Enable the Custom Search API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Custom Search API"
3. Click on the "Custom Search API" result
4. Click "Enable"

## Step 3: Create API Credentials

1. In the Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API Key"
3. Your API key will be displayed. Click "Copy" to copy it
4. Save this key for use in the `.env` file (`IDEASFACTORY_SEARCH_API_KEY`)

## Step 4: Set Up a Custom Search Engine

1. Go to the [Programmable Search Engine Control Panel](https://programmablesearchengine.google.com/controlpanel/all)
2. Click "Add" to create a new search engine
3. Configure your search engine:
   - Enter sites to search (or leave it as "Search the entire web" for general research)
   - Name your search engine
   - Language settings as needed
4. Click "Create"
5. On the next page, click "Control Panel" for your newly created search engine
6. In the control panel, click "Setup" in the sidebar
7. Find the "Search engine ID" field (it will look like `012345678901234567890:abcdefghijk`)
8. Copy this ID for use in the `.env` file (`IDEASFACTORY_SEARCH_ENGINE_ID`)

## Step 5: Configure Your `.env` File

Add the following to your `.env` file:

```
IDEASFACTORY_SEARCH_API_KEY=your_google_api_key_here
IDEASFACTORY_SEARCH_ENGINE_ID=your_search_engine_id_here
```

## Using the Custom Search API

The Google Custom Search API provides 100 search queries per day for free. Beyond that, you will be billed per query. Make sure to check the [pricing details](https://developers.google.com/custom-search/v1/overview#pricing) if you plan to use it extensively.

## Troubleshooting

If you encounter issues with the search functionality:

1. Verify that your API key and search engine ID are correctly entered in the `.env` file
2. Check the Google Cloud Console to ensure the API is enabled
3. Verify that your project has billing enabled if you're using more than 100 queries per day
4. Check the application logs for specific error messages related to the search API

For more information, refer to the [Google Custom Search JSON API documentation](https://developers.google.com/custom-search/v1/overview).

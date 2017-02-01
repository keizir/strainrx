# SRX Search Wizard flow

### 1. Entry point
To enter a search wizard client application send a request to **/search/strain/wizard**.
This only returns and render template located at **pages/search/strain/wizard.html**.
This page includes a wizard steps header and also other required js and css files.
With this page also loads a JS file which initiates an actual wizard: **js/pages/search/strain/search_view.js**.
  
### 2. Wizard description
When *SearchWizard* initializes it retrieves a *UserSetting* named *search_strain_wizard*.
It simply holds a json data with the previous user search. This search is also stored in *UserSearch* object.
Once data retrieved we set it in a **model** object which will be passed to each wizard step.
Then wizard renders a 1st step content. 
When HTML has been rendered wizard restore a previous data state (if user has a previous search).

### 3. Wizard step description
Each search wizard step extends a *SearchWizardStep* JS class.
It base constructor consumes the next option arguments:
- step - a step number in wizard;
- model - a Model object initialized on wizard init step;
- submit_el - a jQuery selector string to select a Submit step button
- skip_el - a jQuery selector string to select a Skip step button
- back_el - a jQuery selector string to select a Back to previous step button
- template_el - a jQuery selector string to select a lodash template

### 4. Wizard flow
After user click the Next button on last step the next requests is fired:
- **/api/v1/user/{user_id}/searches** - persist the latest user search criteria
- **/api/v1/search/strain** - puts a parsed search criteria into session on server
- redirect to **/search/strain/results** route where the **pages/search/strain/search_results.html** template will be rendered
- **/api/v1/search/result/?filter=all**

The last API call is actually doing a search job.
First we gather all query params and a search criteria form a session.
Then we pass all this data to a **SearchElasticService().query_strain_srx_score()** function.
This function builds a ES query and transforms the ES results to a data consumable by a client app.

### 5. ES search query
Along with usual ES query operators SRX search query also runs a Painless language script.
This script calculates a SRX percentage (match score) against each strain in ES index.
This match value will be available as a _score field of each document.
To find script itself see this file under **/web/search/es_service.py** at the bottom of file.

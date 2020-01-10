'use strict';

W.ns('W.pages.search.strain');

W.pages.search.strain.SearchView = function () {

    var Model = W.common.Model,
        SearchWizard = W.pages.search.strain.SearchWizard;

    return {
        init: function () {
            new SearchWizard({
                model: new Model()
            });
        }
    };
}();

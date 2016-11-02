'use strict';

W.ns('W.pages.search.strain');

W.pages.search.strain.SearchWizardStep4 = W.pages.search.strain.SearchWizardStep.extend({

    selectedSideEffects: [],
    renderData: {},

    init: function init(options) {
        this._super({
            step: 4,
            model: options && options.model,
            currentUserId: options && options.currentUserId,
            submit_el: '.btn-step-4',
            skip_el: '.btn-skip-4',
            template_el: '#search-wizard-step4'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        this.clickStrainEffect(this.selectedSideEffects);
        this.clickRemoveEffect(this.selectedSideEffects)
    },

    renderHTML: function renderHTML() {
        return this.$template(this.renderData);
    },

    submit: function submit() {
        var that = this;
        this.showDialogOrProceed(this.selectedSideEffects, function () {
            $.publish('update_step_data', {step: that.step, data: {effects: that.selectedSideEffects}});
            $.publish('submit_form', that.model.getData());
        });
    },

    skip: function skip() {
        $.publish('update_step_data', {step: this.step, data: {skipped: true}});
        $.publish('submit_form', this.model.getData());
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            this.restoreEffectsState(this.step, this.selectedSideEffects);
        }
    }

});
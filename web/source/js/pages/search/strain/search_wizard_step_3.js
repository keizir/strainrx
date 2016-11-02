'use strict';

W.ns('W.pages.search.strain');

W.pages.search.strain.SearchWizardStep3 = W.pages.search.strain.SearchWizardStep.extend({

    selectedBenefits: [],
    renderData: {},

    init: function init(options) {
        this._super({
            step: 3,
            model: options && options.model,
            currentUserId: options && options.currentUserId,
            submit_el: '.btn-step-3',
            skip_el: '.btn-skip-3',
            template_el: '#search-wizard-step3'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        this.clickStrainEffect(this.selectedBenefits);
        this.clickRemoveEffect(this.selectedBenefits)
    },

    renderHTML: function renderHTML() {
        return this.$template(this.renderData);
    },

    submit: function submit() {
        var that = this;
        this.showDialogOrProceed(this.selectedBenefits, function () {
            $.publish('update_step_data', {step: that.step, data: {effects: that.selectedBenefits}});
            $.publish('show_step', {step: 4});
        });
    },

    skip: function skip() {
        $.publish('update_step_data', {step: this.step, data: {skipped: true}});
        $.publish('show_step', {step: 4});
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            this.restoreEffectsState(this.step, this.selectedBenefits);
        }
    }

});
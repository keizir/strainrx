'use strict';

W.ns('W.pages.search.strain');

W.pages.search.strain.SearchWizardStep2 = W.pages.search.strain.SearchWizardStep.extend({

    selectedEffects: [],
    renderData: {},

    init: function init(options) {
        this._super({
            step: 2,
            model: options && options.model,
            currentUserId: options && options.currentUserId,
            submit_el: '.btn-step-2',
            skip_el: '.btn-skip-2',
            template_el: '#search-wizard-step2'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        this.clickStrainEffect(this.selectedEffects);
        this.clickRemoveEffect(this.selectedEffects)
    },

    renderHTML: function renderHTML() {
        return this.$template(this.renderData);
    },

    submit: function submit() {
        var that = this;
        this.showDialogOrProceed(this.selectedEffects, function () {
            $.publish('update_step_data', {step: that.step, data: {effects: that.selectedEffects}});
            $.publish('show_step', {step: 3});
        });
    },

    skip: function skip() {
        $.publish('update_step_data', {step: this.step, data: {skipped: true}});
        $.publish('show_step', {step: 3});
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            this.restoreEffectsState(this.step, this.selectedEffects);
        }
    }

});
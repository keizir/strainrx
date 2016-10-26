'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizard = W.common.Wizard.extend({

    steps: {},

    init: function init(options) {
        this._super({
            model: options && options.model
        });

        this.name = 'SignUpWizard';
        this.showStep({step: 1});

        W.subscribe.apply(this);
    },

    _on_show_step: function _on_show_step(ev, data) {
        this.showStep({step: data.step});
        this.handleStepClick(data.step);
    },

    _on_update_step_data: function _on_update_step_data(ev, data) {
        this.updateData(data);
    },

    _on_submit_form: function _on_submit_form(ev, data) {
        // TODO serialize all data and actually send to backend
    },

    initSteps: function initSteps() {
        this.steps[1] = new W.pages.b2b.SignUpWizardStep1({model: this.model});
        this.steps[2] = new W.pages.b2b.SignUpWizardStep2({model: this.model});
        this.steps[3] = new W.pages.b2b.SignUpWizardStep3({model: this.model});
        this.steps[4] = new W.pages.b2b.SignUpWizardStep4({model: this.model});
        this.steps[5] = new W.pages.b2b.SignUpWizardStep5({model: this.model});
        this.steps[6] = new W.pages.b2b.SignUpWizardStep6({model: this.model});
        this.steps[7] = new W.pages.b2b.SignUpWizardStep7({model: this.model});
        this.steps[8] = new W.pages.b2b.SignUpWizardStep8({model: this.model});
        this.steps[9] = new W.pages.b2b.SignUpWizardStep9({model: this.model});
    },

    showStep: function showStep(data) {
        this.destroy();
        this.show(this.steps[data.step]);
    },

    updateData: function updateData(data) {
        this.model.set(data.step, data.data);
    }

});

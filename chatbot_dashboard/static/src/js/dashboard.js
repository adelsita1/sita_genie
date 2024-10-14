/** @odoo-module **/ //special command for odoo in the begining of the file of js
import {registry} from "@web/core/registry";

const {Component, useState, onWillStart} = owl
import {jsonrpc} from "@web/core/network/rpc_service";
import {useService} from "@web/core/utils/hooks";

// import {onWillStart} from "../../../../../odoo17_c/addons/web/static/lib/owl/owl";

export class ChatbotDashboard extends Component {

    setup() {
        this.action = useService("action")
        this.chatbot_state = useState({
            total_message_sent: 0,
            message_sent_ids: [],
        });
        //this method is called on reload the page call back async
        // overriding this method
        onWillStart(this.onWillStart);

    }

    // Event
    async onWillStart() {
        await this.fetchDataMessages();
    }

    // define the message
    fetchDataMessages() {
        var self = this;
        // function is anonymous  function to handel data get from api
        jsonrpc('/get/messages/data', {}).then(function (data_result) {

            self.chatbot_state.total_message_sent = data_result.total_message_sent;
            self.chatbot_state.message_sent_ids = data_result.message_sent_ids;
        })

    }

//


    _onClickSentMessages() {
        var messages_sent_ids = this.chatbot_state.message_sent_ids
       // way1
        let xml_id=""
        var options={
            clearBreadcrumbs:false, // this for navigation if true no breadcrumbs
            additional_context :{

            } ,
        };
        // this can render even if no id
        //  you can add views like kanban , from , calender
        // view can id can be passed instead of False

        this.action.doAction({
            name: ("Sent Messages"),
            type: 'ir.actions.act_window',
            res_model: 'whatsapp_message_log',
            view_mode: 'form',

            views: [[false, 'list'], [false, 'form']],
            domain: [['id', 'in', messages_sent_ids]],
            context: {
                create: false,
            },
            target: 'current',

        }, options)
        this.action.doAction(xml_id,options)

    }


}

ChatbotDashboard.template = "ChatBotDashBoard" //this is template name in static xml preserve
registry.category("actions").add("chatbot_dashboard_main", ChatbotDashboard) //tag name in dashboard client action
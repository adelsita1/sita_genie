/** @odoo-module **/ //special command for odoo in the begining of the file of js
import { registry } from "@web/core/registry";
const {Component,useState}=owl
export class ChatbotDashboard extends Component{

    setup(){
        this.chatbot_state=useState({
            total_message_sent:1000,
        })
    }
}
ChatbotDashboard.template="ChatBotDashBoard" //this is template name in static xml preserve
registry.category("actions").add("chatbot_dashboard_main",ChatbotDashboard) //tag name in dashboard client action
/** @odoo-module **/  //special command for odoo in the begining of the file of js
import {registry} from "@web/core/registry";
import {jsonrpc} from "@web/core/network/rpc_service";
import {useService} from "@web/core/utils/hooks";
// useRef used for dom hold div or canvas from xml with t-ref
const {Component, useState, onWillStart, onMounted, useRef} = owl

// import {onWillStart} from "../../../../../odoo17_c/addons/web/static/lib/owl/owl";

export class ChatbotDashboard extends Component {
    // use each variables we will used  in setup
    setup() {
        this.action = useService("action")
        this.partner_messages_ref = useRef("partner_messages_ref")
        this.chatbot_state = useState({
            total_message_sent: 0,
            total_message_received: 0,
            total_faq:0,
            message_sent_ids: [],
            message_received_ids: [],
            faqs:[],
            total_agents:0,
            free_agents:0,

        });
        //this method is called on reload the page call back async
        // overriding this method
        onWillStart(this.onWillStart);
        onMounted(this.onMounted);


    }

    // Event
    // called before component is rendered
    async onWillStart() {
        await this.fetchDataMessages();
    }

    // called after loading the component why beacuse I need a selector from the componet so the component must be exist before
    async onMounted() {
        await this.render_total_messages()
        // console.log("in async onMounted")
    }


    // define the message
    fetchDataMessages() {
        var self = this;
        // function is anonymous  function to handel data get from api
        jsonrpc('/get/messages/data', {}).then(function (data_result) {
            console.log("data_result",data_result);
            self.chatbot_state.total_message_sent = data_result.total_message_sent;
            self.chatbot_state.message_sent_ids = data_result.message_sent_ids;
            self.chatbot_state.total_message_received = data_result.total_message_received;
            self.chatbot_state.message_received_ids = data_result.message_received_ids;
            self.chatbot_state.faqs=data_result.faqs;
            self.chatbot_state.total_faq=data_result.total_faq;
            self.chatbot_state.total_agents=data_result.total_agents;
            self.chatbot_state.free_agents=data_result.free_agents;
        })

    }

    async render_total_messages() {
        const result_data = await this.fetchPartnerData();


        const chartData = this.prepareChartData(result_data)

        const $el = $(this.partner_messages_ref.el)
        this.createChart($el, "bar", chartData);

    }

    fetchPartnerData() {
        return jsonrpc("web/dataset/call_kw/whatsapp_message_log/get_message_log", {
            model: 'whatsapp_message_log',
            method: 'get_message_log',
            args: [{}],
            kwargs: {},
        })

    }

    prepareChartData(result_data) {
        const labels = result_data[1];
        const data = result_data[0];
        const colors = generateDynamicColors(5);

        return {
            labels: labels,
            datasets: [{
                label: "Count",
                data: data,
                backgroundColor: colors,
                hoverOffset: 4,
            }]

        }


    };

    createChart(element, type, data) {
        new Chart(
            element, {
                type: type,
                data: data,
            }
        )
    }

    // render_total_messages(){
    //     var self=this;
    //
    //     var ctx=$('.message_direction');
    //     // ctx is the dom or the class which we will assign the chart
    //
    //     // this to call a method from directly add "web/dataset/call_kw/{ModelName}/{FunctionName}
    //     jsonrpc("web/dataset/call_kw/whatsapp_message_log/get_message_log",{
    //         model:'whatsapp_message_log',
    //         method:'get_message_log',
    //         args:[{}],
    //         kwargs:{},
    //     }).then(function (result_data) {
    //         console.log("result_data",result_data);
    //         var data={
    //         labels:result_data[1],
    //         datasets:[{
    //             label:"Count",
    //             data:result_data[0],
    //             backgroundColor:[
    //                 'rgb(255,99,132)',
    //                 'rgb(31,157,213)',
    //                 'rgb(213,198,31)',
    //                 'rgb(213,31,171)',
    //                 'rgb(167,119,7)',
    //                 'rgb(160,19,7)',
    //                 'rgb(7,160,124)',
    //                 'rgb(70,24,20)',
    //                 'rgb(35,149,140)',
    //                 'rgb(7,160,32)',
    //
    //             ], // mapping corresponding
    //         hoverOffset:4,
    //         }],
    //
    //
    //     };
    //         var chart=new Chart(ctx,{
    //         type:'doughnut',
    //         data:data,
    //     })
    //     });
    //
    //     }

    _onClickReceivedMessages() {
        const message_received_ids = this.chatbot_state.message_received_ids;
        const options = {
            clearBreadcrumbs: false,
            additional_context: {},
        }
        this.action.doAction(
            {
                name: ("Message Received"),
                type: 'ir.actions.act_window',
                res_model: "whatsapp_message_log",
                view_mode: "form",
                views: [[false, 'list'], [false, 'form']],
                domain: [['id', 'in', message_received_ids]],
                context: {
                    create: false,
                },
                target: 'current',

            }, options)


    }


    _onClickSentMessages() {
        const messages_sent_ids = this.chatbot_state.message_sent_ids
        // way1
        let xml_id = ""
        const options = {
            clearBreadcrumbs: false, // this for navigation if true no breadcrumbs
            additional_context: {},
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
        // this.action.doAction(xml_id,options)

    }

    _onClickFAQ() {
        const messages_faq = this.chatbot_state.faqs;
        console.log("messages_faq",messages_faq)
        // way1
        let xml_id = ""
        const options = {
            clearBreadcrumbs: false, // this for navigation if true no breadcrumbs
            additional_context: {},
        };
        // this can render even if no id
        //  you can add views like kanban , from , calender
        // view can id can be passed instead of False

        this.action.doAction({
            name: ("FAQs"),
            type: 'ir.actions.act_window',
            res_model: 'question_answer',
            view_mode: 'form',

            views: [[false, 'list']],
            domain: [['id', 'in', messages_faq]],
            context: {
                create: false,
            },
            target: 'current',

        }, options)
        // this.action.doAction(xml_id,options)

    }


}

ChatbotDashboard.template = "ChatBotDashBoard" //this is template name in static xml preserve
registry.category("actions").add("chatbot_dashboard_main", ChatbotDashboard) //tag name in dashboard client action
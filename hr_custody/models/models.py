# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HRCustody(models.Model):
    _name = 'hr.custody'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _description = 'HR Custody'

    def _default_employee(self):
        return self.env.user.employee_id

    STATE_SEL = [
        ("draft", "Draft"),
        ("submit", "Submit"),
        ("hr_approve", "HR Approved"),
        ('return', 'Returned'),
    ]

    name = fields.Char(copy=False, readonly=True, index=True)
    employee_id = fields.Many2one("hr.employee", string="Employee/الموظف", required=True,
                                  default=_default_employee, readonly=True, )
    employee_no = fields.Char(related="employee_id.employee_no", string="Employee Number/رقم الموظف")
    department_id = fields.Many2one('hr.department', string="Department/القسم",
                                    related="employee_id.department_id", readonly=True)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position/الوظيفة",
                                   help="Job position")
    date = fields.Date('Date/التاريخ', readonly=True,
                       default=lambda self: datetime.now())
    custody = fields.Selection(
        [
            ('tangible', 'Tangible Custody'),
            ('non_tangible', 'Other Custody'),
            ('financial_custody', 'Financial Custody'),

        ], 'Custody')
    amount = fields.Float("Amount/المبلغ")
    asset_id = fields.Many2one('account.asset', string="Asset/الأصل")
    is_asset = fields.Boolean(string="is it asset")

    @api.onchange('is_asset')
    def _set_asset_id(self):
        self.asset_id = False

    type_custody = fields.Selection(
        [('mobile', 'Trust of Receiving a Mobile And Sim-Card'),
         ('hand_hold', 'Trust of Receiving Hand Hold Custody '), ('stamp', 'Trust of Receiving And Usage of Stamp '),
         ('journal', 'Trust of Receiving a Locker'),
         ('branch', 'Branch Trust of Receiving Cash Locker Account and ERP Finance User to Issue Receipt Vouchers'),
         ('car', 'Trust of Receiving a Car Or Equipment'),
         ('email', 'Email Account/Device Delivery Form'),
         ], string="Custody Of/نوع العهدة")
    # ('cash', 'Trust of Receiving Cash Locker Account & ERP Finance User to Issue Payment & Receipt Vouchers'),

    other_custody = fields.Selection(
        [('training', 'Custody & Training Contract'),
         ('email', 'Internet Access & Custody Application')], 'Other Custody')

    finance_custody = fields.Selection(
        [('cheque', 'Trust of Receiving a Cheque Receipt Voucher Book'),
         ('loan', 'Loan Request'), ('financial', 'Financial Custody Request')], 'Finance Custody')

    user_id = fields.Many2one('res.users', string='Responsible/المسؤول', required=False,
                              default=lambda self: self.env.user)

    # custody type training fields
    subject = fields.Text(string="Training Subject/التدريب", translate=True)
    trainig_days = fields.Integer(string="No. of Training Days/عدد أيام التدريب")
    start_date = fields.Date(string="Training Start Date/بداية تاريخ التدريب")
    end_date = fields.Date(string="Training End Date/نهاية تاريخ التدريب")
    training_period = fields.Integer(string="Training Period/مدة عهدة التدريب")

    # guarntee type fiedls
    guarntee_employee = fields.Many2one('hr.employee', string="Guarantor Employee/الموظف الضامن")
    guarntee_employee_no = fields.Char(related="guarntee_employee.employee_no",
                                       string="Guarantor Employee Number/رقم الموظف الضامن")
    # chek type fields
    nationality_id = fields.Many2one("res.country", related="employee_id.country_id", string="Nationality/الجنسية")
    identification_id = fields.Char(related="employee_id.identification_id", string="Identification ID/رقم الهوية")
    check_book = fields.Char(string="Check Book/دفتر الشيكات")
    from_no = fields.Integer()
    to_no = fields.Integer()
    # mobile type fields
    mobile_no = fields.Char(string="Mobile No/رقم الموبيل")
    serial_no = fields.Char(string="Serial No/رقم السريل")
    sim_card_no = fields.Char("SIM Card No./رقم الكارت")
    device_status = fields.Text(string="Device Status /حالة الجهاز")

    m_model = fields.Char(string="M Model/الموديل")
    color = fields.Char(string="Color/اللون")
    reciept_date = fields.Datetime(string="Receipt Date/تاريخ استلام")
    headphones = fields.Boolean(string="HeadPhones/سماعات الرأس")
    charger = fields.Boolean(string="شاحن/Charger")
    screen_protection = fields.Boolean(string="Screen Protection/حماية شاشة")
    cover = fields.Boolean(string="Cover/غطاء")
    others = fields.Boolean(string="others/اخر")
    other_test = fields.Text(string="Others/اخر")
    # hand_hold fields
    type_custody_text = fields.Html(string="Mention the custody type/نوع العهدة")
    description = fields.Html(string="Description/الوصف")
    serial = fields.Char(string="Serial Doc No./مسلسل")
    issue_id = fields.Char(string="Issue Entity/الجهة المصدرة")
    issue_date = fields.Date(string="Issue Date/التاريخ")
    expiry_date = fields.Date(string="Expiry Date/تاريخ إنتهاء الصلاحية")

    # stamp type fields
    journal_id = fields.Many2one('account.journal', string="Purpose Of Use/الغرض من الإستخدام")
    journal_code = fields.Char(string="Short Code/الكود")

    company_id = fields.Many2one(comodel_name="res.company", string="Company")

    @api.onchange('journal_id')
    def _get_journal_code(self):
        self.journal_code = self.journal_id.code
        self.account_id = self.journal_id.default_account_id.id

    account_id = fields.Many2one(comodel_name="account.account", string="Default Account/الحساب")
    # account_id = fields.Many2one(comodel_name="", string="", required=False, )
    stamp_image = fields.Binary(string="Stamp Image/الصورة")
    stamp_date = fields.Datetime(string="Stamp Date/تاريخ إستلام الختم")
    box_amount = fields.Float(string="Amount/مبلغ الصندوق")
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency/العملة")
    # journal type fields
    journal_component = fields.Html(string="Locker Current Content/المحتوى الحالي للخزانة")
    journal_amount = fields.Float(string="Journal Amount/مبلغ دفتر اليومية")

    # car type fields
    car_id = fields.Many2one('fleet.vehicle', string="Car Maker/نوع السيارة")
    plate_no = fields.Char(related="car_id.vin_sn", string="Chassis Number/رقم الهيكل")
    car_color = fields.Char(related="car_id.color", string="Color/اللون")
    model = fields.Many2one(related="car_id.model_id", string="Model/الموديل")
    mileage = fields.Float(related="car_id.odometer", string="Last Odometer/آخر عداد المسافات")
    fire = fields.Boolean(string="Fire Ex./نار")
    lifting_tool = fields.Boolean(string="Lifting Tool/أداة الرفع")
    mention_tool = fields.Boolean(string="Mention the Tools/اذكر الأدوات")
    spare = fields.Boolean(string="Spare Wheel/Status/حالة العجة الإحتياطية")
    Mention_other = fields.Boolean(string="Mention Others/اذكر الآخرين")
    car_other = fields.Char(string="Others/الآخر")
    car_status = fields.Text(string="Car Status/حالة السيارة")
    remark = fields.Text(string="Remark/ملاحظة")
    car_image = fields.Binary(string="Car Image/صورة السيارة")
    # email fields
    email_id = fields.Text(string="Email/البريد الإلكتروني")
    justification = fields.Html(string="Justification/التبرير")
    access_category = fields.Selection([('full', 'Full access'),
                                        ('finance', 'Banking and financial'),
                                        ('goverment', 'Government portals'), ('social', 'Social media'),
                                        ('Other', 'Other')], string="Access Category/فئة الوصول")
    other_access = fields.Text('Other Access/وصول آخر')
    access_period = fields.Selection([('permanent', 'Permanent Access'),
                                      ('period', 'Temporary Access')], string="Access Period/فترة الوصول")
    from_date = fields.Date(string="Date From/التاريخ من")
    to_date = fields.Date(string="Date To/التاريخ إلى")
    # financial_custody fields
    advance_amount = fields.Float('Advance Amount SR/المبلغ المقدم ريال')

    move_id = fields.Many2one("account.move", string="Account Move/نقل الحساب")
    state = fields.Selection(STATE_SEL, string="State/الحالة", default="draft", tracking=True)

    custody_receive = fields.Boolean(string="Custody Receive/تسليم العهدة")

    terms_conditions = fields.Text(string="Terms And Conditions/الشروط والاحكام", compute='compute_terms_conditions')
    custody_approve = fields.Boolean(string="Terms And Conditions Approve/الموافقة على الشروط والاحكام")

    financial_custody_amount = fields.Float(string="Amount")

    @api.model
    def _get_additional_terms(self):
        if self.type_custody == 'mobile':
            return """
                                   أقر أنا الموقع أدناه بأنني أطلعت على شروط وضوابط عهدة استلام الجهاز والشريحة كمايلي, وأتعهد بالالتزام بجميع ما ذكر فيها وأكون تحت طائلة المسؤولية
                                   إن الجهاز والشريحة ملكية خاصة لشركة ويستخدم في الأساس لأغراض العمل والهدف من استخدامه رفع كفاءة العمل وسرعة الانجاز وتسهيل مهام العمل
                                   يتعهد الموظف بالمحافظة على الجهاز والشريحة وعدم الإهمال في استخدامها وعدم استخدام أية برامج مقلدة ويتحمل مصاريف الصيانة في حال سوء الاستخدام أو التلف أو مصاريف الاستبدال في حال الفقدان
                                   يتعهد الموظف بعدم استخدام الجهاز والشريحة لغير أغراض العمل وعدم تخزين صور خاصة أو ملفات لا تتعلق بالعمل على الجهاز ويلتزم بالتسليم الفوري للجهاز والشريحة عند الطلب في أي وقت تراه الشركة مناسبا
                                                   يعتبر الموظف مسؤول قانونيا في حال مخالفة نظام الجرائم المعلوماتية المعمول به في المملكة العربية السعودية
                                                   لا يحق للموظف فك أو تعديل أو إضافة أو تبديل قطع غيار للجهاز بنفسه دون موافقة خطية من الشركة
                                                   يتم تسليم الجهاز والشريحة للمدير المباشر أو الموظف البديل وفق محضر تسليم كتابي قبل الاجازة (سواء ادارية أو خاصة)
                    
I hereby confirm that I have read the following terms & conditions of the trust of receiving mobile and sim-card & I undertake to abide by all of what is stated therein & be under liability:
The device and card are privately owned by a company and are primarily used for business purposes and the purpose of its use is to increase work efficiency, speed of delivery and facilitate work tasks.
The employee undertakes to maintain the device and the card and not to neglect in their use and not to use any counterfeit software and bear maintenance costs in case of misuse, damage or replacement expenses in the event of loss.
The employee is legally liable in case of violation of the information crimes system in force in the Kingdom of Saudi Arabia.
The Employee shall not be entitled to disassemble, modify, add or change spare parts for the device by himself without the written consent of the Company.
The device and the card shall be delivered to the direct manager or alternate employee according to a written delivery record before the leave (administrative or private ).
                    """

        elif self.type_custody == 'hand_hold':
            return """
أقر بمايلي:                                                                                                                                                                                                              
    أني استلمت من الشؤون الإدارية بالشركة العهدة العينية المحددة في هذه الوثيقة للاستخدام الخاص بالعمل فقط                                                                                                               
                                                       أني مسؤول مسؤولية تامة عن حسن استخدام االعهدة لأغراض العمل فقط                                                                                                   
                                                       أتعهد بأن لا أتصرف بها إلا ضمن حدود وسياسات الشركة المقرة من قبل الادارة وأن احتفظ بها واحافظ عليها وأن أقوم بتسليمها للشركة عند الطلب في أي وقت أو عند اكتمال, أو انتهاء الغرض منها
                                                       أتعهد بأني اتحمل كافة المسؤولية عن أي فقدان أو نقصان أو سوء استخدام, أو خطأ وأني اتحمل اي ضرر أو مبالغ تترتب على الشركة و اكون تحت طائلة المسائلة والمحاسبة واي مبالغ مترتبة عن ذلك تكون في عهدتي الشخصية وذمتي المالية وان أقوم بسدادها
                                       
confirm the followings:
I received from the Company's Admin affairs the selected hand hold custody to use for Work related purposes only.
I am fully responsible for using it for work only.
I pledge that I will not use the custody except under the company terms and condition and be ready to deliver it anytime upon the company's or upon the completion or the end of its purpose.
I pledge that I bear all responsibility for any loss, decrease, or misuse, mistake, and that I bear any damage or amounts owed to the company and that I will be subject to accountability and accountability and any sums resulting from that will be in my personal custody and financial responsibility and that I pay them.                                                                             

                        """
        elif self.type_custody == 'stamp':
            return """
                             أقر بمايلي:
                             أني استلمت من الشؤون الإدارية بالشركة الختم المذكور أدناه للاستخدام الخاص بالعمل فقط
                             أني اطلعت وعلى دراية بشروط وضوابط عهدة استلام الختم
                             أني مسؤول مسؤولية تامة عن حسن استخدام الختم لأغراض العمل فقط
                             أتعهد بأن لا أتصرف به إلا ضمن حدود العمليات المذكورة أعلاه وضمن حدود وسياسات الشركة المقرة من قبل الادارة وأن احتفظ به واحافظ عليه وأن أقوم بتسليمه للشركة عند الطلب في أي وقت أو عند اكتمال, أو انتهاء الغرض منه
                             أتعهد بأني اتحمل كافة المسؤولية عن أي فقدان أو نقصان أو سوء استخدام, أو خطأ وأني اتحمل اي ضرر أو مبالغ تترتب على الشركة و اكون تحت طائلة المسائلة والمحاسبة واي مبالغ مترتبة عن ذلك تكون في عهدتي الشخصية وذمتي المالية وان أقوم بسدادها

I confirm the followings:
I received from the Company's Admin. affairs a Locker to use for keeping Work related documents and Cash.
I have read the terms and understood conditions of the Trust of Receiving the Locker.
I am fully responsible for its content, and for using it for work only.
I pledge that I will not use the locker balance and to keep the cash in the locker only and be ready to deliver it anytime upon the company's or upon the completion or the end of its purpose.
I pledge to keep the Cash, a copy of every Documents, Receipt Voucher, & Payment Voucher in the Locker.
I pledge to keep evidence of Receipt and Delivery of each document in the Locker.
I pledge that I bear all responsibility for any loss, decrease, or misuse, mistake, and that I bear any damage or amounts owed to the company and that I will be subject to accountability and accountability and any sums resulting from that will be in my personal custody and financial responsibility and that I pay them.
                           """

        elif self.type_custody == 'cash':
            return """
                                     أقر بمايلي:
أني استلمت من الشركة اسم مستخدم وكلمة مرور في نظام الشركة المحاسبي وذلك بغرض اصدار سندات استلام مبالغ نقدية مقبوضة من عملاء الشركة تدخل في حساب الصندوق المذكور أعلاه وتبقى في عهدتي وذمتي المالية لحين سدادها للشركة.
أني اطلعت وعلى دراية بشروط وضوابط استلام صندوق الكاش برقم الحساب المذكور أعلاه والمستخدم في النظام المحاسبي لاصدار سندات قبض مبالغ نقدية من العملاء.
أني مسؤول عنه مسؤولية تامة وعن حسن استخدامه ولأغراض العمل فقط
أتعهد بأن أقوم بتسليم المبالغ المذكورة في رصيد حساب الصندوق عند طلب الشركة, أو عند انتهاء الغرض منه.
أتعهد بأن أقوم بايداع الرصيد بشكل اسبوعي و/أو عندما يصل مبلغ الرصيد في حساب الصندوق مبلغ 10,000.00 عشرة ألاف ريال سعودي وان أتحمل تبعات عدم الالتزام بذلك.
أن احتفظ بصورة كل سند قبض من الزبون واحتفظ بما يثبت ايداع المبالغ في حساب الشركة, أو مايثبت تسليمها للادارة المالية المختصة.
أتعهد بأني اتحمل كافة المسؤولية عن أي فقدان أو نقصان في رصيد حساب الصندوق أو أي خطأ أو سوء استخدام, وأني اتحمل اي ضرر أو مبالغ تترتب على الشركة و اكون تحت طائلة المسائلة القانونية والمحاسبة واي مبالغ مترتبة عن ذلك تكون في عهدتي الشخصية وذمتي المالية وان أقوم بسدادها.

I confirm the followings:
I received from the Company's a Username and Password on ERP financial Module to enable issuing Cash Receipt Vouchers under my financial trust from Company Clients in the above-mentioned Locker Account.
I have read and acknowledge the terms & conditions of the Receipt of the Locker of the a/m account and the user details to issue the Cash Receipt Vouchers from Clients.
I’m fully responsible for it, & for using it properly & for work only
I pledge that I will deliver the cash Balance of the Locker account upon the company's request, or upon the end of its purpose.
I pledge to deposit the account balance weekly &/or when the balance reach’s 10,000.00 ten thousand Saudi Riyals and bear the responsibility of not doing it.
I pledge to keep a copy of each Receipt Voucher and a copy of the deposits in the company Bank account, or evidence of its delivery to the competent financial department.
                                   """

        elif self.type_custody == 'journal':
            return """
                                             أقر بمايلي:
أني استلمت من الشؤون الإدارية بالشركة خزنة لحفظ الكاش الخاص بالعمل و حفظ أية مستندات متعلقة بالعمل.
أني اطلعت وعلى دراية بشروط وضوابط عهدة استلام الخزنة.
أني مسؤول مسؤولية تامة عن محتويات الخزنة وعن حسن استخدامها لأغراض العمل فقط.
أتعهد بأن لا أتصرف بمبلغ رصيد الخزنة وأن احتفظ به في الخزنة فقط و أن أقوم بتسليم الخزنة عند طلب الشركة في أي وقت أو عند اكتمال, أو انتهاء الغرض منها.
أن احتفظ بالمبالغ في الخزنة وبصورة عن كل مستند أو سند قبض أو دفع يودع في الخزنة.
أن احتفظ بما يثبت استلام وتسليم أي مستند أو مبالغ تم ادخالها للخزنة.
أتعهد بأني اتحمل كافة المسؤولية عن أي فقدان أو نقصان أو سوء استخدام, أو خطأ وأني اتحمل اي ضرر أو مبالغ تترتب على الشركة و اكون تحت طائلة المسائلة والمحاسبة واي مبالغ مترتبة عن ذلك تكون في عهدتي الشخصية وذمتي المالية وان أقوم بسدادها.
دواعي استخدام الخزنة لحفظ الوثائق التالية فقط:
□ نقد كاش
□ جوازات لاتمام بعض العمليات
□ دفاتر سند استلام الشيكات ومايثبت استلامها أو تسليمها.

I confirm the followings:
I received from the Company's Admin. affairs a Locker to use for keeping Work related documents and Cash.
I have read the terms and understood conditions of the Trust of Receiving the Locker.
I am fully responsible for its content, and for using it for work only.
I pledge that I will not use the locker balance and to keep the cash in the locker only and be ready to deliver it anytime upon the company's or upon the completion or the end of its purpose.
I pledge to keep the Cash, a copy of every Documents, Receipt Voucher, & Payment Voucher in the Locker.
I pledge to keep evidence of Receipt and Delivery of each document in the Locker.
I pledge that I bear all responsibility for any loss, decrease, or misuse, mistake, and that I bear any damage or amounts owed to the company and that I will be subject to accountability and accountability and any sums resulting from that will be in my personal custody and financial responsibility and that I pay them.
Locker Confirmed Content:
□ Cash 
□ Passports while process of transaction
□ Cheque Receipt Voucher and its receipt/delivery proof
□ Suppliers Documents
□ Cheques while to deposit in Bank or sending to main HO
                                           """
        elif self.type_custody == 'car':
            return """
أقر أنا الموظف المذكور أعلاه بأنني قد عاينت السيارة وفق الحالة الموصوفة أعلاه واستلمتها من الشركة وذلك لإستخدامها في أغراض العمل وأتعهد بالآتي:
عدم استخدامها للمنفعة الشخصية.
المحافظة عليها وعلى ملحقاتها بحالة جيدة.
في حالة حدوث أي مشكلات أن أبلغ الإدارة فوراً.
أقر بمسؤوليتي عن أي تلفيات تحدث للسيارة نتيجة سوء الاستخدام أو عدم العناية.
أقر بأني على علم بمستوى استهلاك الزيوت الحالية للسيارة ومستوى المياه في نظام تبريد الحرارة وموعد تبديلها والصيانة المطلوبة, وأني سوف ألتزم باجراء الصيانة المطلوبة في وقتها وأن اتحمل مسؤولية أي ضرر يلحق للسيارة في حال عن عدم القيام باجراء الصيانة في وقتها.
أن أراعي في استخدامها القوانين وأنظمة المرور المعمول بها في المملكة العربية السعودية.
مسؤوليتي عن أي ضرر ينتج عن مخالفة القوانين وأنظمة المرور والتأمين.
عدم استخدامها من قبل الغير إلا بإذن خطي من الادارة.
عدم قيادة السيارة في حالة انتهاء الرخص و/أو الفحص الدوري وأي رخصة أو فحص أو تأمين أو شهادة يتطلبه نظام المرور السعودي وأتحمل أي مخالفة تنتج عن عدم التقيد بهذا.
     
I, the above-mentioned employee, certify that I inspected the car in accordance with the situation described above and received it from the Company for use in the business purposes. I hereby undertake the following:
Not used for personal benefit.
Keep it and its accessories in good condition.
In the event of any problems, inform the administration immediately.
I acknowledge my responsibility for any damage to the car as a result of misuse or lack of care.
I acknowledge that I have checked the current use of oils for the car, the cooling system water level, and car needed maintenance and I confirm my responsibility for any damage may occur in case of not doing the needed maintenance on time.
I acknowledge my responsibility for any damage to the car as a result of misuse or lack of care.
To take into account in their use the laws and traffic regulations in force in the Kingdom of Saudi Arabia.
I am responsible for any damage resulting from violation of laws, traffic regulations and insurance.
Not to be used by third parties except with the written permission of the administration.
Do not drive the car in case the licenses or regular check-up or insurance are finished and bear any violation resulting from that.
Paying fees for handling incident files for insurance (unless employee endurance is zero)
                                                   """

    @api.model
    def _get_additional_terms_non_tangible(self):
        if self.other_custody == 'training':
            return """
                                         بالتوقيع على هذا العقد، يقبل الموظف المتدرب بقواعد وأنظمة التدريب كمايلي:
أولا: التزامات شركة مشاعل المستقبل                                          
                                         رسوم تسجيل التدريب.
                                         مصاريف الاقامة والمواصلات والوجبات (3 وجبات يوميا).
                                         التذاكر ورسوم تأشيرة السفر والخروج والعودة.
                                         يعتبر الراتب الشهري للموظف المتدرب مستحق في حالة الحضور والالتزام بالتدريب.
                                         ثانيا: التزامات الموظف المتدرب
                                         الالتزام بالحضور في الاوقات المحددة للتدريب.
                                         تحمل مصاريف ونفقات ورسوم التدريب في حالة عدم الالتحاق بالتدريب أو عدم الحضور أو الفشل أو عدم النجاح بنسبة أقل من 70% أو في حالة انتهاء العلاقة العمالية بناء على طلب الموظف خلال مدة لاتقل عن (18) شهر من تاريخ العودة للعمل بعد التدريب.
                                         
    
By signing this contract, the trainee employee accepts the training rules & regulations as follows:
First: Mashail Future Obligations
Training registration fee.
Accommodation, transportation and meals expenses (3 meals per day (.
Tickets, Travel Visa, exit & re-entry Visa fees.
The monthly salary of the trainee employee is considered to be payable in the event of attendance & commitment to training.
Second: Obligations of the trainee employee
Commitment to attendance at specific training times.
To bear the expenses and fees of the training in the event of in the case of non-enrolment in the training, lack of attendance, failure or failure to achieve less than 70% or in case of termination of the Labor relationship at the request of the employee within a period of not less than (18) months from the date of return to work after training
                                       
                                       """

        elif self.other_custody == 'email':
            return """
                              بتوقيعي على الطلب، أقر بأنني قرأت وفهمت سياسة استخدام الانترنت في الشركة كما هو مرفق ضمن هذا النموذج وبأنني سأستخدم الانترنت وفقاً للاحتياجات الموضحة بهذا الطلب بما يتوافق مع سياسة الشركة.

Signing on the application form, I hereby confirm that I have read and fully understood the Company Internet Usage Policy and that I will use the internet according to the requirements specified in this form and instructed in the mentioned policy.
                                                   """

    @api.model
    def _get_additional_terms_financial_custody(self):

        if self.finance_custody == 'cheque':
            return """
                                                 أنا الموظف المذكور أعلاه من الجنسية جنسية الموظف رقم الإقامة/الهوية رقم الهوية أقر بمايلي:
        أني استلمت من الشؤون الإدارية بالشركة دفتر سند استلام شيكات عدد (رقم) رقم تسلسل من رقم الى رقم                                          
                                                 أني اطلعت على شروط وضوابط عهدة استلام دفتر سندات استلام الشيكات.
                                                 أني مسؤول عنه مسؤولية تامة.
                                                 أتعهد بأني أقوم بتسليمه عند طلب الشركة أو عند اكتمال استخدام السندات كاملة, أو عند انتهاء الغرض منه.
                                                 أن احتفظ بصورة كل شيك او مستند يتم استلامه مرفق مع كل سند.
                                                 أن احتفظ بما يثبت ايداع الشيك أو المستند في حساب الشركة البنكي أو مايثبت تسليمها للادارة المالية المختصة.
                                                 أتعهد بأني اتحمل كافة المسؤولية عن أي فقدان او نقصان أو سوء استخدام, وأني اتحمل اي ضرر أو مبالغ تترتب على الشركة و اكون تحت طائلة المسائلة والمحاسبة واي مبالغ مترتبة عن ذلك تكون في عهدتي الشخصية وذمتي المالية وان أقوم بسدادها.
                                                 

I’m the aforementioned employee of the nationality employee nationality ID/Residence Permit No. Iqama number.I confirm the followings:
I received from the Company's Admin. affairs a Cheque Receipt Voucher Book number (number) serial from (number) to (number)
I have read the terms and conditions of the custody of the Cheque Receipt Vouchers Book.
I am fully responsible for it.
I pledge that I will deliver it upon the company's request or upon the completion of use, or upon the end of its purpose.
I pledge to keep a copy of every Cheque or document received attached to each Receipt Voucher.
I pledge to keep evidence of depositing the Cheque or document in the Company's Bank account, or evidence of its delivery to the competent financial department.
I pledge that I bear all responsibility for any loss, decrease, or misuse, and that I bear any damage or amounts owed to the company and that I will be subject to accountability and accountability and any sums resulting from that will be in my personal custody and financial responsibility and that I pay them.
                                               """

        elif self.finance_custody == 'loan':
            return """
                                                         انا الموظف الكفيل الضامن:
                اكفل زميلي الموظف المذكور اسمه أعلاه كفالة أداء وغرم في حالة تأخر أو عدم سداد المبلغ المذكور أدناه.                                         

I’m the guarantor employee:
By this I guarantee my colleague as mentioned above, in performance and fine payment in case of delay or failure to pay the loan amount as mentioned below.
                                                       """
        elif self.finance_custody == 'financial':
            return """
                                                                 بهذا أقدم طلبي للحصول على المبلغ المذكور أعلاه كعهدة مالية في ذمتي وأتعهد بتقديم أصول فواتير الأعمال والخدمات والمشتريات المتعلقة في صرف مبلغ العهدة. 

This is my application for the above amount as a financial trust in my debt and I undertake to provide the assets of business invoices, services and related purchases relating to the payment of the amount of the trust.                                                       """

    @api.depends('custody', 'type_custody', 'other_custody', 'finance_custody')
    def compute_terms_conditions(self):
        for rec in self:
            rec.terms_conditions = ''
            if rec.custody == 'tangible':
                rec.terms_conditions = self._get_additional_terms()

            elif rec.custody == 'non_tangible':
                rec.terms_conditions = self._get_additional_terms_non_tangible()

            elif rec.custody == 'financial_custody':
                rec.terms_conditions = self._get_additional_terms_financial_custody()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.custody') or _('New')
        rec = super(HRCustody, self).create(vals)
        return rec

    def action_submit(self):
        for rec in self:
            rec.state = 'submit'

            template = self.env['ir.model.data']._xmlid_lookup('hr_custody.email_template_submit_hr_custody_mail')[2]

            if template and rec.employee_id.user_id.share:
                email_template_obj = self.env['mail.template'].browse(
                    template)
                data = {'email_to': rec.employee_id.user_id.email}
                values = email_template_obj.with_context(data).generate_email(rec.id,
                                                                              ['subject', 'body_html', 'email_from',
                                                                               'email_to',
                                                                               'partner_to', 'email_cc', 'reply_to',
                                                                               'scheduled_date'])
                msg_id = self.env['mail.mail'].create(values)

                if msg_id:
                    msg_id._send()
            else:
                rec.activity_schedule('mail.mail_activity_data_todo', user_id=self.employee_id.user_id.id)

    def action_approve(self):
        for rec in self:
            rec.state = 'hr_approve'

            if not rec.custody_approve:
                raise UserError('يجب الموافقة على الشروط والاحكام ')

            if not rec.department_id.analytic_account_id and self.asset_id:
                raise UserError('يجب إدخال الحساب التحليلي داخل القسم')

            if self.is_asset and self.asset_id and self.asset_id.depreciation_move_ids:
                for line in self.asset_id.depreciation_move_ids:
                    if line.state == 'draft':
                        for move in line.line_ids:
                            move.analytic_account_id = rec.department_id.analytic_account_id

    def action_set_to_draft(self):
        for rec in self:
            # rec.created = False 
            rec.state = 'draft'

            for r in rec.return_id:
                r.state = 'cancel'

    def unlink(self):
        if self.state in ['hr_approve', 'return']:
            raise UserError('You can not delete this request..!')

        self.created = False
        return super(HRCustody, self).unlink()

    return_id = fields.One2many('hr.custody.return', 'custody_id')
    return_count = fields.Integer(compute='_compute_return_count')
    created = fields.Boolean(copy=False)

    def _compute_return_count(self):
        """ Compute the number of return record """
        for ev in self:
            ev.return_count = 0
            ev.return_count = len(ev.return_id)

    def action_view_custody_return(self):

        return_id = self.mapped('return_id')

        action_vals = {
            'name': _('HR Custody Return'),
            'domain': [('id', 'in', return_id.ids)],
            'view_type': 'form',
            'res_model': 'hr.custody.return',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(return_id) > 0:
            action_vals.update({'res_id': return_id[0].id, 'view_mode': 'tree,form'})
        else:
            action_vals.update({'view_mode': 'form',
                                'context': {
                                    "default_custody_id": self.id,
                                    "default_employee_id": self.employee_id.id

                                }})
        return action_vals

    def action_custody_return(self):
        self.ensure_one()

        return_id = self.env['hr.custody.return'].create({
            'user_id': self.user_id.id,
            'custody_id': self.id,
            'date': fields.Date.today(),
            'employee_id': self.employee_id.id,
            'car_id': self.car_id.id,
            'remark': self.remark,
            'asset_id': self.asset_id.id,

        })

        self.return_id.write({'custody_id': self.id})
        self.created = True
        self.message_post(body=_("HR Custody Return Created"))

        return self.action_view_custody_return()


class AccountJournal(models.Model):
    _inherit = "account.journal"

    code = fields.Char()


class HRCustodyReturn(models.Model):
    _name = 'hr.custody.return'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _description = 'HR Custody Return'

    def _default_employee(self):
        return self.env.user.employee_id

    STATE_SEL = [
        ("draft", "Draft"),
        ("submit", "Submit"),
        ("hr_approve", "Returned"),
        ('cancel', 'Cancelled'),
    ]

    name = fields.Char(copy=False, readonly=True, index=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True,
                                  default=_default_employee, readonly=True, )
    employee_no = fields.Char(related="employee_id.employee_no")
    department_id = fields.Many2one('hr.department', string="Department",
                                    related="employee_id.department_id", readonly=True)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position",
                                   help="Job position")
    date = fields.Date('Date', readonly=True,
                       default=lambda self: datetime.now())
    custody_id = fields.Many2one('hr.custody')
    custody = fields.Selection(related="custody_id.custody")

    type_custody = fields.Selection(related="custody_id.type_custody")
    other_custody = fields.Selection(related="custody_id.other_custody")
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)

    # car type fields
    car_id = fields.Many2one('fleet.vehicle', readonly=True)
    plate_no = fields.Char(related="car_id.vin_sn")
    car_color = fields.Char(related="car_id.color")
    model = fields.Many2one(related="car_id.model_id")
    mileage = fields.Float(related="car_id.odometer")
    fire = fields.Boolean(related="custody_id.fire")
    lifting_tool = fields.Boolean(related="custody_id.lifting_tool")
    mention_tool = fields.Boolean(related="custody_id.mention_tool")
    spare = fields.Boolean(related="custody_id.spare")
    Mention_other = fields.Boolean(related="custody_id.Mention_other")
    car_other = fields.Char(related="custody_id.car_other")
    car_status = fields.Text(related="custody_id.car_status")
    remark = fields.Text(related="custody_id.remark")

    check_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Car Returned as Receipt Status")
    state = fields.Selection(STATE_SEL, string="State", default="draft", tracking=True)
    # mobile
    asset_id = fields.Many2one('account.asset', readonly=True)
    mobile_no = fields.Char(related="custody_id.mobile_no")
    serial_no = fields.Char(related="custody_id.serial_no")

    m_model = fields.Char(related="custody_id.m_model")
    color = fields.Char(related="custody_id.color")
    reciept_date = fields.Datetime(string="Receipt Date")
    headphones = fields.Boolean(related="custody_id.headphones")
    charger = fields.Boolean(related="custody_id.charger")
    screen_protection = fields.Boolean(related="custody_id.screen_protection")
    cover = fields.Boolean(related="custody_id.cover")
    others = fields.Boolean(related="custody_id.others")
    other_test = fields.Text(related="custody_id.other_test")
    m_check_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Mobile Returned as Receipt Status")

    def action_submit(self):
        for rec in self:
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            rec.state = 'hr_approve'
            if rec.custody_id:
                rec.custody_id.state = 'return'

    def action_set_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            self.custody_id.created = False
            self.custody_id.state = 'hr_approve'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.custody.return') or _('New')
        rec = super(HRCustodyReturn, self).create(vals)
        return rec

    def unlink(self):
        if self.state in ['hr_approve', 'cancel']:
            raise UserError('You can not delete this request..!')

        self.custody_id.created = False
        return super(HRCustodyReturn, self).unlink()

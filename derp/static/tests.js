uR.ready(function() {
    uC.data = uC.data || {};
    uC.data.emails = [
        // < 5s
        'John.Elsey@richardson.com',
        'dmiadmin@dminc.com',
        'jfong@strozfriedberg.com',
        'lkeares@peoplelinx.com',
        'rdemuth@frontlineselling.com',//7
        'peternicholson@boaweb.com',
        'phill.keene@octiv.com',
        'rchinapen@ringlead.com',

        //> 30s
        'paola.hemmingsen@woodmac.com',
        'ypavlish@intralinks.com',
        'DMulligan@iso.com',
        'jscheer@daviesmurphy.com',//3
        'cblake@kings.com',//3
        'nicole.nummela@perkinelmer.com',
        'Matthew.Sykes@tatacommunications.com',//2
        'Elizabeth.hatchel@fiserv.com',
        'kyle.lovan@greenwayhealth.com',
        'Rachel.Spates@sunlife.com',//2 
    ]

    uC.data.urls = [
        //reverse('api:admin-report-engagement',args=['shares','2014-01-13','2017-11-13']),
        //'/api/cards/pending/', '/api/cards/completed/', '/api/cards/dismissed/',
        //'/api/cards/totals/',
        //'/api/optimizations/totals/',
        //'/api/optimizations/completed/',
        //'/api/timeline/?cutoff_date=2017-11-03T02:50:11',
        //'/api/articles/new/','/api/articles/shared/','/api/articles/dismissed/',
        //'/api/users/leaderboard',
        {
            url: "/api/users/manager/deals",
            get: [
                "deal_state=open&",
                "deal_state=closed&top_percent=20",
                "deal_state=closed&end_date=2017-12-06&start_date=2015-06-23&unit_grain=year",
                "deal_state=closed&end_date=2017-12-09&start_date=2017-10-28&unit_grain=week",
                "deal_state=closed&end_date=2017-12-09&start_date=2017-12-03&unit_grain=day",
                "deal_state=open&end_date=2018-06-11&start_date=2017-12-11",
                "deal_state=closed&end_date=2017-10-23&start_date=2017-04-23&team_id=1283",
                "deal_state=closed&end_date=2017-10-23&start_date=2017-04-23&team_id=1263",
                "deal_state=closed&end_date=2017-10-24&start_date=2017-04-24&team_id=1280",
            ],
            group: "API",
        },
        {
            url: "/api/users/dashboard/clicks",
            get: [
                "end_date=&start_date=&unit_back=6&unit_grain=day",
                "end_date=&start_date=&unit_back=6&unit_grain=week",
                "end_date=&start_date=&unit_back=6&unit_grain=month",
            ],
            group: "Dash Clicks",
            skip: true,
        },
        {
            url: "/api/users/dashboard/shares",
            get: [
                "end_date=&start_date=&unit_back=month&unit_grain=month",
                "end_date=&start_date=&unit_back=6&unit_grain=week",
                "end_date=&start_date=&unit_back=6&unit_grain=day",
            ],
            group: "Dash Shares",
            skip: true,
        },
    ];

    uC.data.urls.forEach(function(url) {
        if (url.skip) { return }
        uR.forEach(uC.data.emails,function(email) {
            function _t() {
                var test = this;
                test.do();
                test.ajax({
                    url:"/api/v1/auth/login-session/",
                    fields: ['username','password'],
                    method: "post",
                    data: {username: email, password: 'password1'},
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    },
                });
                if (typeof url == "string") { url = { url: url } }
                (url.get || ['']).forEach(function(query_string) {
                    test.ajax({
                        url: url.url+"?"+query_string,
                        allow: [404,403],
                    })
                })
            }
            _t._name = url.group+": "+email
            konsole.addCommands(_t)
        })
    })
})

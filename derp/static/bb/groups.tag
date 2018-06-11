uR.getDerp = function () {
    uR.ajax({
        url: "/derp/results.json",
        success: function(data,response) {
            uR.derp = data;
            data.commits = {};
            data.command_group_map = {};
            data.command_test_map = {};
            data.groups = data.group_list.reduce(function(acc,group,i) {
                acc[group.id] = group;
                group.status_count = uR.zeros(data.commit_list.length);
                group.order = i;
                uR.forEach(group.commands,function(command) {
                    data.command_group_map[command] = group;
                });
                return acc;
            }, {});
            uR.forEach(data.commit_list,function(commit,i) {
                data.commits[commit.id] = commit;
                commit.order = i;
            });
            uR.forEach(data.status_list,function(status) {
                var commit = data.commits[status.commit_id];
                var test = data.tests[status.test_id];
                var command = test.parameters.url;
                var group = data.command_group_map[command];
                if (!group) { return }
                data.groups[group.id].status_count[commit.order]++;
            })
        },
    })
}


<bb-table>
    <table>
        <tr>
            <th each={ h in header }>{ h }</th>
        </tr>
        <tr each={ rows }>
            <yield />
        </tr>
    </table>

    this.on("mount",function() {
        this.header = this.opts.header || this.parent.header;
        this.rows = this.opts.rows || this.parent.rows;
    })
    
</bb-table>

<bb-groups>
    <bb-table>
        <td><a href="#group-{ id }">{ name }</a></td>
        <td>{ commands.length }</td>
        <td each={ c in status_count }>{ c } / { data.targets._all.length * commands.length }</td>
    </bb-table>
    this.on("mount",function() {
        this.rows = [];
        this.header = ["Test Group","# Commands"]
        uR.forEach(data.commit_list,function(commit,i) { self.header.push(commit.name) });
        this.rows = data.derp.group_list;
        this.update();
    });
</bb-groups>

<bb-group-detail>
    <bb-table></bb-table>

    this.on("mount", function () {
        uR.ajax({
            url: "/derp/group.json?id="+this.opts.data[0],
            success: function(data,response) {
                this.data = data;
                this.headers = ['Email'];
                uR.forEach(data.hashes
            },
        });
    })
</bb-group-detail>
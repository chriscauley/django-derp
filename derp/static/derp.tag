<derp-table>
    <table class="table">
        <tr>
            <th></th>
            <th each={opts.commit_list}>{name}</th>
        </tr>
        <tr each={opts.group_list}>
            <td>
                {url_name}
                <div if={ qs}>?{qs}</div>
            </td>
            <td each={r in runs}>{r} / {parent.parent.opts.total_targets}</td>
        </tr>
    </table>

    this.on("mount",function(){
        this.update();
    });
</derp-table>

uR.ready(function() {
    uR.math = {};
    uR.math.average = function(numbers) {
        if (!numbers || !numbers.length) { return }
        var total = 0;
        var length = numbers.length || 1;
        for (var i=0;i<numbers.length;i++) { total += numbers[i]; }
        return {
            mean: total/length,
            count: numbers.length,
        }
    }
    function makeChart(x,ys,labels) {
        var canvas = document.createElement("canvas")
        canvas.id="my_chart";
        document.body.appendChild(canvas);
        var ctx = canvas.getContext('2d');
        var datasets = [];
        var colors = [
            'rgb(255, 99, 132)',
            'rgb(0, 99, 132)',
        ];
        uR.forEach(ys,function(y,i) {
            datasets.push({
                label: labels[i],
                borderColor: colors[i],
                data: [0, 10, 5, 2, 20, 30, 45],
            })
        });
        var chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: x,
                datasets: datasets,
            },
            options: {}
        });
    }
    uR.ajax({
        url: "/derp/results.json",
        success: function(data) {
            function zeros(n){
                var out = [];
                for (var i=0;i<n;i++) { out.push(0) }
                return out;
            }
            uR.derp = data;
            data.test_groups = {};
            data.test_list = [];
            data.total_targets = 0;
            var group_map = {}, group_list = [], hash_list = [], commits={};
            data.group_list = group_list;
            uR.forEach(data.commit_list,function(commit) {
                commits[commit.id] = commit;
                hash_list.push(commit.id);
            })
            for (var target_group in data.targets) { data.total_targets += data.targets[target_group].length }
            for (var test_id in data.tests) {
                var test = data.tests[test_id];
                data.test_list.push(test);
                var url = test.parameters.url;
                if (!data.test_groups[url]) {
                    var _parts = url.split("?");
                    data.test_groups[url] = {
                        url_name: test.url_name,
                        runs: zeros(hash_list.length),
                        url: _parts[0],
                        qs: _parts[1],
                    }
                    group_list.push(data.test_groups[url]);
                }
                group_map[test_id] = data.test_groups[url];
            }
            uR.forEach(data.status_list,function(status) {
                group_map[status.test_id].runs[hash_list.indexOf(status.commit_id)] += 1
            });
            data.mount_to="#content";
            //uR.mountElement('derp-table',data);
        },
    });

});

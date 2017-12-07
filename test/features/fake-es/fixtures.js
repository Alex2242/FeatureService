
// fs stands for FeatureService



/******************************************************************************
                        fixtures utils functions
*****************************************************************************/

var makeErrorFixture = function(describe, FSEndpoint) {
  return {
      describe: describe,
      FSEndpoint: FSEndpoint,
      expectedFSResult: {
          status: 400
      }
  };
}

var fakeTimeserie = function(from,steps,stepDuration) {
    var fromDate = new Date(from);
    return { items: [...Array(steps).keys()].map(idx => {
            return {
                timestamp: (new Date(fromDate.getTime() +
                    (idx * stepDuration * 1000))).toISOString(),
                val: Math.random()
            };
        })
    }
}

var makeid = function () {
    var id = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for (var i = 0; i < 16; i++)
        id += possible.charAt(Math.floor(Math.random() * possible.length));

    return id;
}

var fakeTimeserieTob = function(from,steps,stepDuration) {
    var fromDate = new Date(from);
    return { items: [...Array(steps).keys()].map(idx => {
            return {
                timestamp: (new Date(fromDate.getTime() +
                    (idx * stepDuration * 1000))).toISOString(),
                val: [...Array(50)].map( elem => Math.random())
            };
        })
    }
}

var fakeEsResponse = function(timeSerie,esIndex) {
    var esRes = {
        "took" : 5,
        "timed_out" : false,
        "_shards" : {
            "total" : 5,
            "successful" : 5,
            "skipped" : 0,
            "failed" : 0
        },
        "hits" : {
            "total" : timeSerie.items.length,
            "max_score" : 1.0,
            "hits" : [
            ]
        }
    };

    timeSerie.items.forEach(function(tsItem, index, array) {
        var hit = {
            "_index" : esIndex,
            "_type" : "data",
            "_id" : makeid(),
            "_score" : 1.0,
            "_source" : {
                "timestamp" : tsItem.timestamp,
                "val" : tsItem.val
            }
        };
        esRes.hits.hits.push(hit);


    });

    return esRes;

}

/******************************************************************************
                            fixtures
*****************************************************************************/

var getAllFixtures = [

    {
        describe: 'return 200 and results for get-all with sample ts',
        fsEndpoint: '/data.ebdo.org/v1/search/get-all',
        expectedIndex: "fakeIndex",
        expectedEsQuery: {"size":10000,"query":{"match_all":{}}},
        esResult: fakeEsResponse(fakeTimeserie("2017-12-01T12:00:00.000Z",120,60),"fakeTobIndex")
        //expectedFSResult: makeTopEditorsPerEditsAqsResult('all-editor-types', 'all-page-types', 'daily')
    }

]

var rangeQueryFixtures = [
    {
        describe: 'return 200 and results for get-all with sample ts',
        fsEndpoint: '/data.ebdo.org/v1/search/get-all',
        expectedIndex: "fakeTobIndex",
        expectedEsQuery: {
            size: 10000,
            query: {
                range: {
                    timestamp: {
                        gte: "2017-12-01T12:00:00.000Z",
                        lt: "2017-12-01T20:00:00.000Z"
                    }
                }
            },
            sort: [
                { timestamp: { order: "asc" } }
            ]
        },
        esResult: fakeEsResponse(fakeTimeserieTob("2017-12-01T12:00:00.000Z",120,60),"fakeTobIndex")
        //expectedFSResult: makeTopEditorsPerEditsAqsResult('all-editor-types', 'all-page-types', 'daily')
    }
]


exports.values = []
    .concat(getAllFixtures)
    .concat(rangeQueryFixtures)
    ;

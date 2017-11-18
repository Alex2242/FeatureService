/* Copyright (C) 2017 Project-EBDO
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * EBDO-FeatureService Seqrch functions
 * Author:
 */
'use strict';

var HyperSwitch = require('hyperswitch');
const URI = HyperSwitch.URI;
var path = require('path');
var fsUtil = require('../lib/FeatureServiceUtil');

var spec = HyperSwitch.utils.loadSpec(path.join(__dirname, 'examples.yaml'));





const STEP_TO_SECONDS = {
    second:    1,
    minute:   60,
    hour:   3600,
    day:   86400
};



class ExampleOfTimeserieTreament {
    // Class that handles timeseries requests

    constructor(options) {
        this.options = options;
        this.elastic_search = options.elastic_search;
    }

    function requestURI(elastic_search) {
        if (elastic_search) {
            const scheme = (elastic_search.scheme) ? `${elastic_search.scheme}://` : '';
            const host = elastic_search.host || '';
            const port = (elastic_search.port) ? `:${elastic_search.port}` : '';
            const index = elastic_search.index || '';

            return `${scheme}${host}${port}/${index}`;
        } else { // Fail with 500 if elastic_search conf is not set
            throw new HTTPError({
                status: 500,
                body: {
                    type: 'internal_error',
                    detail: 'Druid configuration not set',
                }
            });
        }
    }


    fakeTimeserie(hyper, req) {
        var requestParams = req.params;
        let uri = this.requestURI(this.elastic_search);
        fsUtil.validateFromAndTo(requestParams);

        var fromDate = requestParams.fromDate;
        var intervalSeconds = (requestParams.toDate - fromDate) / 1000;
        var stepSeconds = STEP_TO_SECONDS[requestParams.step];

        if (stepSeconds > intervalSeconds) {
            fsUtil.throwIfNeeded('Step should be smaller than [from, to[ interval');
        }

        var stepNumbers = intervalSeconds / stepSeconds;

        return fsUtil.normalizeResponse({
            status: 200,
            body: {
                items: [...Array(stepNumbers).keys()].map(idx => {
                    return {
                        ts: (new Date(fromDate.getTime() +
                            (idx * stepSeconds * 1000))).toISOString(),
                        val: Math.random()
                    };
                })
            }
        });
    }


    meanTimeserie(hyper, req) {
        // Returns mean of the timeserie specified in the request

        var requestParams = req.params;
        fsUtil.validateFromAndTo(requestParams);

        // Build the uri used to request the timeserie
        const uriFakeTS = new URI([requestParams.domain, 'sys', 'examples',
            'fake-timeserie',requestParams.from,
            requestParams.to,requestParams.step]);

        var response = fsUtil.normalizeResponse({
                status: 200,
                body: {
                    items: {
                        startts: requestParams.fromDate,
                        endts: requestParams.toDate,
                        length: -1,
                        mean: -1 // return the mean in the response
                    }
                }
            });

        /*
        return hyper.get({ uri: uriFakeTS }).then((res) => {
                    res.status = 200;
                    res.body = { items: {
                        startts: requestParams.fromDate,
                        endts: requestParams.toDate,
                        length: res.body.items.length,
                        mean: res.body.items.map(items => items.val).
                            reduce((prev, next) => prev + next, 0) / res.body.items.length
                        }};
                }
            );*/

        // Request the timeserie, wait for the response and modify the response
        // in order to put the correct values in it.
        hyper.get({ uri: uriFakeTS }).then((res) => {
                response.body.items.mean = res.body.items.map(items => items.val).
                    reduce((prev, next) => prev + next, 0) / res.body.items.length;
                response.body.items.length = res.body.items.length;
            });

        return response;
    }
}

module.exports = function(options) {
    var tst = new ExampleOfTimeserieTreament(options);

    return {
        spec: spec,
        operations: {
            fakeTimeserie: tst.fakeTimeserie.bind(tst),
            meanTimeserie: tst.meanTimeserie.bind(tst)
        }
    };
};

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
 * EBDO-FeatureService Search functions
 * Author:
 */
'use strict';

var HyperSwitch = require('hyperswitch');
const URI = HyperSwitch.URI;
var path = require('path');
const HTTPError = HyperSwitch.HTTPError;
var spec = HyperSwitch.utils.loadSpec(path.join(__dirname, 'search.yaml'));



class Search {
    // Class meant to provide internal endpoints able to query Elasticsearch

    constructor(options) {
        this.options = options;
        this.elasticSearch = options.elasticSearch;
    }

    static requestURI(elasticSearch) {
        // Generate an incomplete uri that points to Elasticsearch
        if (elasticSearch) {
            const scheme = (elasticSearch.scheme) ? `${elasticSearch.scheme}://` : '';
            const host = elasticSearch.host || '';
            const port = (elasticSearch.port) ? `:${elasticSearch.port}` : '';
            const path = elasticSearch.path || '';

            return `${scheme}${host}${port}${path}`;
        } else { // Fail with 500 if elasticSearch conf is not set
            throw new HTTPError({
                status: 500,
                body: {
                    type: 'internal_error',
                    detail: 'Elasticsearch configuration not set',
                }
            });
        }
    }


    getAll(hyper, req) {
        // Requests Elasticsearch with an empty search at a given index
        // ie: gets all documents at the given index
        var requestParams = req.params;
        const incompleteUri = Search.requestURI(this.elasticSearch);
        const esUri = incompleteUri + '/' + requestParams.index + '/_search';

        var query = JSON.stringify({
            size: 10000,
            query: {
                    match_all: {}
                }
        });

        return hyper.get({
                            uri: esUri,
                            headers: { "Content-Type": "application/json" },
                            body: query })
            .then((res) => {
                            res.body = { items: res.body.hits.hits.map((hit) => hit._source) };
                            return res;
                        })
            .catch((err) => err);
    }

    rangeQuery(hyper,req) {
        // Requests Elasticsearch with a time based range query on a index

        var requestParams = req.params;
        const incompleteUri = Search.requestURI(this.elasticSearch);
        const esUri = incompleteUri + '/' + requestParams.index + '/_search';

        var query = JSON.stringify({
            size: 10000,
            query: {
                range: {
                    timestamp: {
                        gte: requestParams.from,
                        lt: requestParams.to
                    }
                }
            },
            sort: [
                { timestamp: { order: "asc" } }
            ]
        });

        return hyper.get({
                            uri: esUri,
                            headers: { "Content-Type": "application/json" },
                            body: query })
            .then((res) => {
                            res.body = { items: res.body.hits.hits.map((hit) => hit._source) };
                            return res;
                        })
            .catch((err) => err);
    }

}


module.exports = function(options) {
    var search = new Search(options);

    return {
        spec: spec,
        operations: {
            getAll: search.getAll.bind(search),
            rangeQuery: search.rangeQuery.bind(search)
        }
    };
};

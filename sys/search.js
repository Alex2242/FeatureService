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
        this.elastic_search = options.elastic_search;

    }

    static requestURI(elastic_search) {
        // Generate an incomplete uri that points to Elasticsearch
        if (elastic_search) {
            const scheme = (elastic_search.scheme) ? `${elastic_search.scheme}://` : '';
            const host = elastic_search.host || '';
            const port = (elastic_search.port) ? `:${elastic_search.port}` : '';

            return `${scheme}${host}${port}`;
        } else { // Fail with 500 if elastic_search conf is not set
            throw new HTTPError({
                status: 500,
                body: {
                    type: 'internal_error',
                    detail: 'Elasticsearch configuration not set',
                }
            });
        }
    }

    static esRequest(hyper,req,query,elastic_search) {
        // Requests Elasticsearch with the given ES DSL query

        var requestParams = req.params;

        // Create an incomplete uri which points to Elasticsearch
        const incompleteUri = Search.requestURI(elastic_search);

        // Complete the uri with the DSL query
        // if the request is made on all indices, pass _all as index
        const searchUri = incompleteUri + '/' + requestParams.index +
            '/_search?source_content_type=application/json&source='+ JSON.stringify(query);

        // return Elasticsearch response (this needs modifications)
        return hyper.get({ uri: searchUri }).catch( (e) => console.log(e) );
    }

    getAll(hyper, req) {
        // Requests Elasticsearch with an empty search at a given index
        // ie : gets all documents at the given index

        var query =
            { "query" :
                {
                    "match_all":
                        {}
                }
            };

        return Search.esRequest(hyper,req,query,this.elastic_search);
    }

    rangeQuery(hyper,req) {
        // Requests Elasticsearch with a range query on a index
        // returns all documents whithin the range

        var requestParams = req.params;

        var query = {
            "size": 100,
            "query" : {
                "range": {
                    "timestamp": {
                         "gte" : requestParams.from,
                         "lt" : requestParams.to
                    }
                }
            },
            "sort": [
                { "timestamp" : {"order" : "asc"} }
            ]
         };

        return Search.esRequest(hyper,req,query,this.elastic_search);
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

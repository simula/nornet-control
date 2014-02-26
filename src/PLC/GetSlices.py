from PLC.Method import Method
from PLC.Parameter import Parameter, Mixed
from PLC.Filter import Filter
from PLC.Auth import Auth
from PLC.Persons import Person, Persons
from PLC.Nodes import Nodes
from PLC.Sites import Site, Sites
from PLC.Slices import Slice, Slices

class GetSlices(Method):
    """
    Returns an array of structs containing details about slices. If
    slice_filter is specified and is an array of slice identifiers or
    slice names, or a struct of slice attributes, only slices matching
    the filter will be returned. If return_fields is specified, only the
    specified details will be returned.

    Users may only query slices of which they are members. PIs may
    query any of the slices at their sites. Admins and nodes may query
    any slice. If a slice that cannot be queried is specified in
    slice_filter, details about that slice will not be returned.
    """

    roles = ['admin', 'pi', 'user', 'node']

    accepts = [
        Auth(),
        Mixed([Mixed(Slice.fields['slice_id'],
                     Slice.fields['name'])],
              Parameter(str,"name"),
              Parameter(int,"slice_id"),
              Filter(Slice.fields)),
        Parameter([str], "List of fields to return", nullok = True)
        ]

    returns = [Slice.fields]

    def call(self, auth, slice_filter = None, return_fields = None):
        # If we are not admin, make sure to return only viewable
        # slices.
#        if isinstance(self.caller, Person) and \
#           'admin' not in self.caller['roles']:
#            # Get slices that we are able to view
#            valid_slice_ids = self.caller['slice_ids']
#            # pis can view all slices at their site
#            if 'pi' in self.caller['roles'] and self.caller['site_ids']:
#                sites = Sites(self.api, self.caller['site_ids'])
#                for site in sites:
#                    valid_slice_ids += site['slice_ids']
#            # techs can view all slices on the nodes at their site
#            if 'tech' in self.caller['roles'] and self.caller['site_ids']:
#                nodes = Nodes(self.api, {'site_id': self.caller['site_ids']}, ['site_id', 'slice_ids'])
#                for node in nodes:
#                    valid_slice_ids.extend(node['slice_ids'])
#
#            if not valid_slice_ids:
#                return []
#
#            if slice_filter is None:
#                slice_filter = valid_slice_ids

        # Must query at least slice_id (see below)
        if return_fields is not None and 'slice_id' not in return_fields:
            return_fields.append('slice_id')
            added_fields = True
        else:
            added_fields = False

        slices = Slices(self.api, slice_filter, return_fields)

        # Filter out slices that are not viewable
#        if isinstance(self.caller, Person) and \
#           'admin' not in self.caller['roles']:
#            slices = filter(lambda slice: slice['slice_id'] in valid_slice_ids, slices)

        # Remove slice_id if not specified
        if added_fields:
            for slice in slices:
                if 'slice_id' in slice:
                    del slice['slice_id']

        return slices

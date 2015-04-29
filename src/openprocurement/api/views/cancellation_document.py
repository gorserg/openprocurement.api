# -*- coding: utf-8 -*-
from logging import getLogger
from cornice.resource import resource, view
from openprocurement.api.utils import (
    get_file,
    save_tender,
    upload_file,
    apply_patch,
    error_handler,
    update_journal_handler_params,
    update_file_content_type,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)


LOGGER = getLogger(__name__)


@resource(name='Tender Cancellation Documents',
          collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
          path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
          description="Tender cancellation documents",
          error_handler=error_handler)
class TenderCancellationDocumentResource(object):

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db

    @view(renderer='json', permission='view_tender')
    def collection_get(self):
        """Tender Cancellation Documents List"""
        cancellation = self.request.validated['cancellation']
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in cancellation['documents']]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in cancellation['documents']
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @view(renderer='json', validators=(validate_file_upload,), permission='edit_tender')
    def collection_post(self):
        """Tender Cancellation Document Upload
        """
        if self.request.validated['tender_status'] in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.request.validated['cancellation'].documents.append(document)
        if save_tender(self.request):
            update_journal_handler_params({'document_id': document.id})
            LOGGER.info('Created tender cancellation document {}'.format(document.id), extra={'MESSAGE_ID': 'tender_cancellation_document_create'})
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @view(renderer='json', permission='view_tender')
    def get(self):
        """Tender Cancellation Document Read"""
        if self.request.params.get('download'):
            return get_file(self.request)
        document = self.request.validated['document']
        document_data = document.serialize("view")
        document_data['previousVersions'] = [
            i.serialize("view")
            for i in self.request.validated['documents']
            if i.url != document.url
        ]
        return {'data': document_data}

    @view(renderer='json', validators=(validate_file_update,), permission='edit_tender')
    def put(self):
        """Tender Cancellation Document Update"""
        if self.request.validated['tender_status'] in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.request.validated['cancellation'].documents.append(document)
        if save_tender(self.request):
            LOGGER.info('Updated tender cancellation document {}'.format(self.request.context.id), extra={'MESSAGE_ID': 'tender_cancellation_document_put'})
            return {'data': document.serialize("view")}

    @view(content_type="application/json", renderer='json', validators=(validate_patch_document_data,), permission='edit_tender')
    def patch(self):
        """Tender Cancellation Document Update"""
        if self.request.validated['tender_status'] in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            LOGGER.info('Updated tender cancellation document {}'.format(self.request.context.id), extra={'MESSAGE_ID': 'tender_cancellation_document_patch'})
            return {'data': self.request.context.serialize("view")}

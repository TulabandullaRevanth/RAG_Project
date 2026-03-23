class RBACSystem:
    def __init__(self):
        # Permissions Mapping: {role: {department: status}}
        # status: 'Full', 'Summary', 'None', 'Own'
        self.permissions = {
            'admin': {
                'Finance': 'Full',
                'Legal': 'Full',
                'HR': 'Full'
            },
            'manager': {
                'Finance': 'Full',
                'Legal': 'Summary',
                'HR': 'Full'
            },
            'employee': {
                'Finance': 'None',
                'Legal': 'None',
                'HR': 'Own'
            },
            'auditor': {
                'Finance': 'Full',
                'Legal': 'Full',
                'HR': 'None'
            }
        }

    def filter_documents(self, documents, role, user_id=None):
        """
        Filters 'documents' list based on the user 'role' and 'user_id' (for HR records).
        """
        if role not in self.permissions:
            return []
            
        role_perms = self.permissions[role]
        filtered_docs = []
        
        for doc in documents:
            dept = doc['metadata'].get('department')
            if not dept:
                continue
            
            # Default to allow General access
            if dept == 'General':
                filtered_docs.append(doc)
                continue
                
            if dept not in role_perms:
                continue
                
            perm_status = role_perms[dept]
            
            if perm_status == 'Full':
                filtered_docs.append(doc)
            elif perm_status == 'Summary':
                # Mark doc for summarization only
                doc['metadata']['access_type'] = 'Summary'
                filtered_docs.append(doc)
            elif perm_status == 'Own':
                doc_owner = doc['metadata'].get('user_id')
                # For 'Own' records, we allow if the doc is marked 'ALL' (public) OR matches user_id
                if doc_owner == 'ALL' or (user_id and doc_owner == user_id):
                    filtered_docs.append(doc)
            elif perm_status == 'None':
                continue
                
        return filtered_docs

    def is_authorized(self, role, department):
        if role == 'admin': return True
        return self.permissions.get(role, {}).get(department) != 'None'

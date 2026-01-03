-- Grant ACL for UTL_INADDR to app_user
-- This must run as SYSTEM or user with DBA privileges

BEGIN
  -- Grant execute on UTL_INADDR package
  BEGIN
    EXECUTE IMMEDIATE 'GRANT EXECUTE ON UTL_INADDR TO app_user';
    DBMS_OUTPUT.PUT_LINE('[+] Granted EXECUTE on UTL_INADDR to app_user');
  EXCEPTION
    WHEN OTHERS THEN
      DBMS_OUTPUT.PUT_LINE('[!] Error granting EXECUTE: ' || SQLERRM);
  END;
  
  -- Create ACL for network access
  BEGIN
    -- Drop existing ACL if exists
    BEGIN
      DBMS_NETWORK_ACL_ADMIN.DROP_ACL(acl => 'app_user_acl.xml');
    EXCEPTION
      WHEN OTHERS THEN NULL;
    END;
    
    -- Create new ACL
    DBMS_NETWORK_ACL_ADMIN.CREATE_ACL(
      acl         => 'app_user_acl.xml',
      description => 'ACL for app_user to use UTL_INADDR',
      principal   => 'APP_USER',
      is_grant    => TRUE,
      privilege   => 'resolve'
    );
    
    -- Assign ACL to all hosts
    DBMS_NETWORK_ACL_ADMIN.ASSIGN_ACL(
      acl  => 'app_user_acl.xml',
      host => '*'
    );
    
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('[+] ACL created and assigned to app_user');
  EXCEPTION
    WHEN OTHERS THEN
      DBMS_OUTPUT.PUT_LINE('[!] Error creating ACL: ' || SQLERRM);
  END;
END;
/
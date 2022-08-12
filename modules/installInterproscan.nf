/*
 * Install Interproscan
 */
process installInterproscan {

    input:


    output:
    path "${interproscan_db}"

    script:
    interproscan_link=params.interproscan_link
    tarball=params.interproscan_tarball
    interproscan_db=params.interproscan_db
    lsf=params.lsf

    """
    wget ${interproscan_link}
    wget ${interproscan_link}.md5
    md5sum -c ${tarball}.md5
    tar -pxvzf ${tarball}
    cd ${interproscan_db}

    # Edit interproscan.properties file
    sed -i 's/\${bin.directory}\\/prosite\\/pfscan/pfscan/' interproscan.properties
    sed -i 's/\${bin.directory}\\/prosite\\/pfsearch/pfsearch/' interproscan.properties
    sed -i 's/pfsearch_wrapper.py/\${bin.directory}\\/prosite\\/pfsearch_wrapper.py/' interproscan.properties

    python3 initial_setup.py
    cd ..
    """
}

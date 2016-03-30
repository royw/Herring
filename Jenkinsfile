stage name: 'setup tools', concurrency: 1
node('linux') {
    // clone more resent repo to workspace
    git url: 'https://github.com/royw/Herring.git', branch: 'master'

    // make sure python environment is current
    sh '''
        cd ~/.herring/herringlib && git pull origin master
        sudo pip install --upgrade pip
        sudo pip install --upgrade setuptools
        sudo pip install --upgrade herring
    '''
}

stage name: 'setup dev environment', concurrency: 1
node('linux') {
    // create/update virtual environments
    herring 'project::mkvenvs'
    herring 'project::upvenvs'

    // remove any previous build artifacts
    herring 'clean'
}

stage 'build'
// create packages
node('linux') {
    herring 'build'
}

stage 'doc'
// build documentation
node('linux') {
    herring 'doc'
}

stage 'QA'
node('linux') {
    // unit test in workspace
    herring 'test'

    // unit test packages in virtual environments
    herring 'tox'

    // generate metrics
    herring 'metrics'
    herring 'metrics::sloccount'
}

def herring(task) {
    echo "herring ${task}"
    sh "herring ${task}"
}

stage 'publish'
node('linux') {
    // make the source package (sdist) available on job page
    step([$class: 'ArtifactArchiver', artifacts: 'dist/*.tar.gz', fingerprint: true])

    // TODO: upload packages to local pypi server

    // publish documentation to sidebar
    publishHTML(target: [allowMissing: false, keepAll: true, reportDir: 'build/docs', reportFiles: 'index.html', reportName: 'Herring Documentation'])

    // copy documentation to web server /docs on local machine
    // TODO: use a publisher?
    def name = "${env.JOB_NAME}"
    sh """
        mkdir -p /var/www/docs/${name}.new
        cp -r build/docs/* /var/www/docs/${name}.new/
        rm -rf /var/www/docs/${name}
        mv /var/www/docs/${name}.new /var/www/docs/${name}
    """
}
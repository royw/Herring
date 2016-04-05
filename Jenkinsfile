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

stage name: 'setup environment', concurrency: 1
node('linux') {
    // create/update virtual environments
    herring 'project::mkvenvs'
    herring 'project::upvenvs'

    // remove any previous build artifacts
    herring 'clean'
}

stage 'build'
// create packages
parallel(
    package: {
        node('linux') {
            herring 'build'

            // make the source package (sdist) available on job page
            step([$class: 'ArtifactArchiver', artifacts: 'dist/*.tar.gz,installer/*installer.sh', fingerprint: true])

            // TODO: upload packages to local pypi server
        }
    }, QA: {
        node('linux') {
            herring 'doc'

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

    }, metrics: {
        node('linux') {
            // unit test in workspace
            herring 'test'

            // unit test packages in virtual environments
            herring 'tox'

            // generate metrics
            herring 'metrics'
            herring 'metrics::sloccount'

            // publish metrics results
            step([$class: 'CcmPublisher', pattern: 'quality/*.xml'])

            // doesn't work: slocCount pattern: 'quality/sloccount.sc'
            // doesn't work: step([$class: 'SloccountPublisher', pattern: 'quality/sloccount.sc'])
        }
    }
)


def herring(task) {
    echo "herring ${task}"
    sh "herring ${task}"
}


// 3D Network Background Animation
console.log('Network background script loaded');

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing network background');
    
    var c = document.getElementById('network-canvas');
    if (!c) {
        console.error('Canvas element not found!');
        return;
    }
    
    console.log('Canvas found, setting up animation');
    
    var w = c.width = window.innerWidth,
        h = c.height = window.innerHeight,
        ctx = c.getContext('2d'),
        
        opts = {
            range: 250,
            baseConnections: 5,
            addedConnections: 5,
            baseSize: 9,
            minSize: .25,
            dataToConnectionSize: .33,
            sizeMultiplier: .7,
            allowedDist: 60,
            baseDist: 99,
            addedDist: 77,
            connectionAttempts: 100,
            
            dataToConnections: .5,
            baseSpeed: .0005,
            addedSpeed: .0495,
            baseGlowSpeed: .1,
            addedGlowSpeed: .4,
            
            rotVelX: .003,
            rotVelY: .002,
            
            repaintColor: '#000',
            connectionColor: '#8B5CF6', // Purple theme color
            dataColor: '#8B5CF6', // Purple theme color
            
            wireframeWidth: .33,
            wireframeColor: '#333',
            
            depth: 300,
            focalLength: 550,
            vanishPoint: {
                x: w / 2,
                y: h / 2
            }
        },
        
        squareRange = opts.range * opts.range,
        squareAllowed = opts.allowedDist * opts.allowedDist,
        mostDistant = opts.depth + opts.range,
        sinX = sinY = 0,
        cosX = cosY = 0,
        
        connections = [],
        data = [],
        all = [],
        tick = 0,
        totalProb = 0,
        
        Tau = Math.PI * 2;

    // Handle window resize
    window.addEventListener('resize', function() {
        w = c.width = window.innerWidth;
        h = c.height = window.innerHeight;
        opts.vanishPoint.x = w / 2;
        opts.vanishPoint.y = h / 2;
    });

    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, w, h);
    console.log('Canvas initialized, starting animation in 100ms');

    window.setTimeout(init, 100);

    function init() {
        console.log('Initializing 3D network');
        var connection = new Connection(0, 0, 0, opts.baseSize);
        connections.push(connection);
        all.push(connection);
        connection.link();
        
        console.log('Starting animation loop');
        anim();
    }

    function Connection(x, y, z, size) {
        this.x = x;
        this.y = y;
        this.z = z;
        this.size = size;
        
        this.screen = {};
        
        this.links = [];
        this.probabilities = [];
        this.isEnd = false;
        
        this.glowSpeed = opts.baseGlowSpeed + opts.addedGlowSpeed * Math.random();
    }

    Connection.prototype.link = function() {
        if (this.size < opts.minSize)
            return this.isEnd = true;
        
        var links = [],
            connectionsNum = opts.baseConnections + Math.random() * opts.addedConnections | 0,
            attempt = opts.connectionAttempts,
            
            alpha, beta, len,
            cosA, sinA, cosB, sinB,
            pos = {},
            passedExisting, passedBuffered;
        
        while (links.length < connectionsNum && --attempt > 0) {
            alpha = Math.random() * Math.PI;
            beta = Math.random() * Tau;
            len = opts.baseDist + opts.addedDist * Math.random();
            
            cosA = Math.cos(alpha);
            sinA = Math.sin(alpha);
            cosB = Math.cos(beta);
            sinB = Math.sin(beta);
            
            pos.x = len * cosA * sinB;
            pos.y = len * sinA * sinB;
            pos.z = len * cosB;
            
            if (pos.x * pos.x + pos.y * pos.y + pos.z * pos.z < squareRange) {
                passedExisting = true;
                passedBuffered = true;
                
                for (var i = 0; i < connections.length; ++i)
                    if (squareDist(pos, connections[i]) < squareAllowed)
                        passedExisting = false;

                if (passedExisting)
                    for (var i = 0; i < links.length; ++i)
                        if (squareDist(pos, links[i]) < squareAllowed)
                            passedBuffered = false;

                if (passedExisting && passedBuffered)
                    links.push({ x: pos.x, y: pos.y, z: pos.z });
            }
        }
        
        if (links.length === 0)
            this.isEnd = true;
        else {
            for (var i = 0; i < links.length; ++i) {
                var pos = links[i],
                    connection = new Connection(pos.x, pos.y, pos.z, this.size * opts.sizeMultiplier);
                
                this.links[i] = connection;
                all.push(connection);
                connections.push(connection);
            }
            for (var i = 0; i < this.links.length; ++i)
                this.links[i].link();
        }
    }

    Connection.prototype.step = function() {
        this.setScreen();
        var opacity = .1 + (1 - this.screen.z / mostDistant) * .4;
        this.screen.color = `rgba(139, 92, 246, ${opacity})`;
        
        for (var i = 0; i < this.links.length; ++i) {
            ctx.moveTo(this.screen.x, this.screen.y);
            ctx.lineTo(this.links[i].screen.x, this.links[i].screen.y);
        }
    }

    Connection.prototype.draw = function() {
        ctx.fillStyle = this.screen.color;
        ctx.beginPath();
        ctx.arc(this.screen.x, this.screen.y, this.screen.scale * this.size, 0, Tau);
        ctx.fill();
    }

    function Data(connection) {
        this.glowSpeed = opts.baseGlowSpeed + opts.addedGlowSpeed * Math.random();
        this.speed = opts.baseSpeed + opts.addedSpeed * Math.random();
        
        this.screen = {};
        
        this.setConnection(connection);
    }

    Data.prototype.reset = function() {
        this.setConnection(connections[0]);
        this.ended = 2;
    }

    Data.prototype.step = function() {
        this.proportion += this.speed;
        
        if (this.proportion < 1) {
            this.x = this.ox + this.dx * this.proportion;
            this.y = this.oy + this.dy * this.proportion;
            this.z = this.oz + this.dz * this.proportion;
            this.size = (this.os + this.ds * this.proportion) * opts.dataToConnectionSize;
        } else
            this.setConnection(this.nextConnection);
        
        this.screen.lastX = this.screen.x;
        this.screen.lastY = this.screen.y;
        this.setScreen();
        var opacity = .2 + (1 - this.screen.z / mostDistant) * .6;
        this.screen.color = `rgba(139, 92, 246, ${opacity})`;
    }

    Data.prototype.draw = function() {
        if (this.ended)
            return --this.ended;
        
        ctx.beginPath();
        ctx.strokeStyle = this.screen.color;
        ctx.lineWidth = this.size * this.screen.scale;
        ctx.moveTo(this.screen.lastX, this.screen.lastY);
        ctx.lineTo(this.screen.x, this.screen.y);
        ctx.stroke();
    }

    Data.prototype.setConnection = function(connection) {
        if (connection.isEnd)
            this.reset();
        else {
            this.connection = connection;
            this.nextConnection = connection.links[connection.links.length * Math.random() | 0];
            
            this.ox = connection.x;
            this.oy = connection.y;
            this.oz = connection.z;
            this.os = connection.size;
            
            this.nx = this.nextConnection.x;
            this.ny = this.nextConnection.y;
            this.nz = this.nextConnection.z;
            this.ns = this.nextConnection.size;
            
            this.dx = this.nx - this.ox;
            this.dy = this.ny - this.oy;
            this.dz = this.nz - this.oz;
            this.ds = this.ns - this.os;
            
            this.proportion = 0;
        }
    }

    Connection.prototype.setScreen = Data.prototype.setScreen = function() {
        var x = this.x,
            y = this.y,
            z = this.z;
        
        // apply rotation on X axis
        var Y = y;
        y = y * cosX - z * sinX;
        z = z * cosX + Y * sinX;
        
        // rot on Y
        var Z = z;
        z = z * cosY - x * sinY;
        x = x * cosY + Z * sinY;
        
        this.screen.z = z;
        
        // translate on Z
        z += opts.depth;
        
        this.screen.scale = opts.focalLength / z;
        this.screen.x = opts.vanishPoint.x + x * this.screen.scale;
        this.screen.y = opts.vanishPoint.y + y * this.screen.scale;
    }

    function squareDist(a, b) {
        var x = b.x - a.x,
            y = b.y - a.y,
            z = b.z - a.z;
        
        return x * x + y * y + z * z;
    }

    function anim() {
        window.requestAnimationFrame(anim);
        
        ctx.fillStyle = opts.repaintColor;
        ctx.fillRect(0, 0, w, h);
        
        ++tick;
        
        var rotX = tick * opts.rotVelX,
            rotY = tick * opts.rotVelY;
        
        cosX = Math.cos(rotX);
        sinX = Math.sin(rotX);
        cosY = Math.cos(rotY);
        sinY = Math.sin(rotY);
        
        if (data.length < connections.length * opts.dataToConnections && Math.random() < .1) {
            var datum = new Data(connections[0]);
            data.push(datum);
            all.push(datum);
        }
        
        ctx.beginPath();
        ctx.lineWidth = opts.wireframeWidth;
        ctx.strokeStyle = opts.wireframeColor;
        all.map(function(item) { item.step(); });
        ctx.stroke();
        all.sort(function(a, b) { return b.screen.z - a.screen.z });
        all.map(function(item) { item.draw(); });
    }
    
    console.log('Network background setup complete');
});